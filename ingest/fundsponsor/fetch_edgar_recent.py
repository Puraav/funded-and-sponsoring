"""Fetch the last N days of Form D filings straight from EDGAR (for the radar).

The quarterly Form D data sets lag by up to three months. This reads the SEC's daily form
index, downloads each new Form D's `primary_doc.xml` (cached on disk) and writes one flat
parquet file. Filtering to Bay Area startups happens in dbt.
"""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import requests
from lxml import etree

from . import config
from .http import download

SCHEMA = pa.schema(
    [
        ("accession_number", pa.string()),
        ("filing_date", pa.date32()),
        ("submission_type", pa.string()),
        ("cik", pa.string()),
        ("entity_name", pa.string()),
        ("street1", pa.string()),
        ("city", pa.string()),
        ("state", pa.string()),
        ("zipcode", pa.string()),
        ("entity_type", pa.string()),
        ("industry_group", pa.string()),
        ("is_business_combination", pa.bool_()),
        ("first_sale_date", pa.date32()),
        ("amount_offered", pa.float64()),
        ("amount_sold", pa.float64()),
        ("officers", pa.string()),
    ]
)


def index_rows(text: str) -> list[dict]:
    """Rows of a daily form index whose form type is exactly `D` (not `D/A`)."""
    found = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 5 or parts[0] != "D" or not parts[-1].startswith("edgar/data/"):
            continue
        path, filed, cik = parts[-1], parts[-2], parts[-3]
        found.append(
            {
                "cik": cik,
                "accession": Path(path).stem,
                "filing_date": datetime.datetime.strptime(filed, "%Y%m%d").date(),
            }
        )
    return found


def _text(node, path: str) -> str | None:
    value = node.findtext(path)
    return value.strip() if value and value.strip() else None


def _money(value: str | None) -> float | None:
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None  # "Indefinite"


def _date(value: str | None) -> datetime.date | None:
    try:
        return datetime.date.fromisoformat(value) if value else None
    except ValueError:
        return None


def parse_form_d(xml: bytes, accession: str, filing_date: datetime.date) -> dict:
    """Pull the fields the models need out of one Form D `primary_doc.xml`."""
    root = etree.fromstring(xml)
    issuer = root.find("primaryIssuer")
    offering = root.find("offeringData")
    officers = []
    for person in root.iterfind("relatedPersonsList/relatedPersonInfo"):
        roles = [r.text.strip() for r in person.iterfind(".//relationship") if r.text]
        if "Executive Officer" not in roles:
            continue
        first = _text(person, "relatedPersonName/firstName")
        last = _text(person, "relatedPersonName/lastName")
        officers.append(" ".join(part for part in (first, last) if part))
    return {
        "accession_number": accession,
        "filing_date": filing_date,
        "submission_type": _text(root, "submissionType"),
        "cik": (_text(issuer, "cik") or "").zfill(10),
        "entity_name": _text(issuer, "entityName"),
        "street1": _text(issuer, "issuerAddress/street1"),
        "city": _text(issuer, "issuerAddress/city"),
        "state": _text(issuer, "issuerAddress/stateOrCountry"),
        "zipcode": _text(issuer, "issuerAddress/zipCode"),
        "entity_type": _text(issuer, "entityType"),
        "industry_group": _text(offering, "industryGroup/industryGroupType"),
        "is_business_combination": _text(
            offering, "businessCombinationTransaction/isBusinessCombinationTransaction"
        )
        == "true",
        "first_sale_date": _date(_text(offering, "typeOfFiling/dateOfFirstSale/value")),
        "amount_offered": _money(_text(offering, "offeringSalesAmounts/totalOfferingAmount")),
        "amount_sold": _money(_text(offering, "offeringSalesAmounts/totalAmountSold")),
        "officers": "; ".join(officers) or None,
    }


def business_days(days: int, today: datetime.date) -> list[datetime.date]:
    span = [today - datetime.timedelta(days=offset) for offset in range(days + 1)]
    return [d for d in reversed(span) if d.weekday() < 5]


def fetch_index(day: datetime.date, agent: str) -> list[dict]:
    """Form D rows of one day's index. Holidays and not-yet-published days have none."""
    cached = config.EDGAR_DIR / "index" / f"form.{day:%Y%m%d}.idx"
    if not cached.exists():
        url = config.EDGAR_DAILY_INDEX.format(
            year=day.year, quarter=(day.month - 1) // 3 + 1, yyyymmdd=f"{day:%Y%m%d}"
        )
        try:
            if not download(url, cached, user_agent=agent):
                return []
        except requests.HTTPError as error:
            if error.response is not None and error.response.status_code == 403:
                return []  # the SEC answers 403 for a day with no index
            raise
    return index_rows(cached.read_text(errors="replace"))


def write_parquet(records: list[dict], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(records, schema=SCHEMA), dest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=30, help="how many days back to read")
    args = parser.parse_args()
    agent = config.sec_user_agent()

    # a filing with co-issuers is listed once per issuer; keep one line per accession
    by_accession: dict[str, dict] = {}
    for day in business_days(args.days, datetime.date.today()):
        for row in fetch_index(day, agent):
            by_accession.setdefault(row["accession"], row)
    listed = list(by_accession.values())
    print(f"Form D filings listed in the last {args.days} days: {len(listed):,}")

    records, failed = [], 0
    for number, row in enumerate(listed, 1):
        cached = config.EDGAR_DIR / "formd" / f"{row['accession']}.xml"
        url = config.EDGAR_PRIMARY_DOC.format(
            cik=row["cik"], accession=row["accession"].replace("-", "")
        )
        try:
            if not download(url, cached, user_agent=agent):
                failed += 1
                continue
            records.append(parse_form_d(cached.read_bytes(), row["accession"], row["filing_date"]))
        except (requests.RequestException, etree.XMLSyntaxError, AttributeError):
            failed += 1
        if number % 500 == 0:
            print(f"  {number:,} of {len(listed):,} read")

    write_parquet(records, config.FORMD_RECENT_PARQUET)
    california = sum(1 for r in records if r["state"] == "CA")
    dates = [r["filing_date"] for r in records]
    print(f"Parsed {len(records):,} filings ({failed} could not be read); {california:,} in CA")
    if dates:
        print(f"Filing dates: {min(dates)} to {max(dates)}")
    print(f"Saved {config.FORMD_RECENT_PARQUET}")


if __name__ == "__main__":
    main()
