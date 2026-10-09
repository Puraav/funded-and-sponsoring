"""Export the radar: web/public/data/radar.json and radar/radar_YYYY-MM-DD.md.

Reads only the `radar` table, so it also runs in the weekly GitHub Action, where the rest of
the warehouse does not exist. Company page links come from the committed companies.json.
"""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path

import duckdb

from . import config
from .export_site import rows, write

SITE_ROWS = 50
MARKDOWN_ROWS = 25


def page_slugs(web_data_dir: Path) -> dict[str, str]:
    """CIK → slug for startups that have their own page on the site."""
    index = web_data_dir / "companies.json"
    if not index.exists():
        return {}
    return {c["cik"]: c["slug"] for c in json.loads(index.read_text()) if c.get("has_page")}


def money(value) -> str:
    if not value:
        return "not disclosed"
    return f"${value / 1e6:,.1f}M" if value >= 1e6 else f"${value / 1e3:,.0f}K"


def build(warehouse: duckdb.DuckDBPyConnection, web_data_dir: Path, today: datetime.date) -> dict:
    slugs = page_slugs(web_data_dir)
    radar = rows(
        warehouse,
        f"""select rank, accession, cik, company, city, county_name as county, industry,
                   filing_date, amount_sold, round_bin, score, reasons, lcas_24m, sec_url
            from radar order by rank limit {SITE_ROWS}""",
    )
    for row in radar:
        row["slug"] = slugs.get(row["cik"])
    span = warehouse.execute(
        "select min(filing_date), max(filing_date), count(*) from int_recent_raises"
    ).fetchone()
    return {
        "generated": today.isoformat(),
        "days": (span[1] - span[0]).days + 1 if span[0] else None,
        "first_filing": span[0].isoformat() if span[0] else None,
        "last_filing": span[1].isoformat() if span[1] else None,
        "startups_considered": span[2],
        "rows": radar,
    }


def markdown(radar: dict) -> str:
    lines = [
        f"# Radar, {radar['generated']}",
        "",
        f"Bay Area startups that filed a Form D between {radar['first_filing']} and "
        f"{radar['last_filing']}, ranked by H-1B filing history "
        f"({radar['startups_considered']} startups considered). Score is 0 to 100: up to 40 for "
        "H-1B filings in the 24 months before the raise, 25 if any were for software, data or "
        "product roles, 15 if any were early-career (Level I or II), and up to 20 for the "
        "amount raised. A high score means the company sponsored recently and just raised "
        "money, not that it has open roles.",
        "",
        "| # | Company | City | Raised | Score | Why | Filing |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in radar["rows"][:MARKDOWN_ROWS]:
        lines.append(
            f"| {row['rank']} | {row['company']} | {(row['city'] or '').title()} | "
            f"{money(row['amount_sold'])} | {row['score']} | {row['reasons']} | "
            f"[Form D]({row['sec_url']}) |"
        )
    return "\n".join(lines) + "\n"


def export(warehouse, web_data_dir: Path, radar_dir: Path, today: datetime.date) -> dict:
    radar = build(warehouse, web_data_dir, today)
    write(web_data_dir / "radar.json", radar)
    radar_dir.mkdir(parents=True, exist_ok=True)
    (radar_dir / f"radar_{today.isoformat()}.md").write_text(markdown(radar))
    return radar


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--top", type=int, default=10, help="rows to print")
    args = parser.parse_args()
    today = datetime.date.today()
    with duckdb.connect(str(config.WAREHOUSE), read_only=True) as warehouse:
        radar = export(warehouse, config.WEB_DATA_DIR, config.RADAR_DIR, today)
    print(
        f"Radar for {radar['first_filing']} to {radar['last_filing']}: "
        f"{radar['startups_considered']} startups considered\n"
    )
    for row in radar["rows"][: args.top]:
        place = (row["city"] or "").title()
        print(f"{row['rank']:>2}. [{row['score']:>3}] {row['company']} ({place}), "
              f"raised {money(row['amount_sold'])}\n      {row['reasons']}")  # fmt: skip
    print(f"\nWrote web/public/data/radar.json and radar/radar_{today.isoformat()}.md")


if __name__ == "__main__":
    main()
