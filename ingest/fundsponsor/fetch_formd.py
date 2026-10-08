"""Download the SEC Form D quarterly data sets into data/raw/formd/*.parquet.

Only downloads and parses: every quarter's tab-delimited tables are read as strings, stacked,
given a `quarter` column and saved as parquet. Filtering and modelling happen in dbt.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

import pandas as pd

from . import config
from .http import download

DATE_COLUMNS = {"FORMDSUBMISSION": ["FILING_DATE"], "OFFERING": ["SALE_DATE"]}
MONEY_COLUMNS = {"OFFERING": ["TOTALOFFERINGAMOUNT", "TOTALAMOUNTSOLD"]}


def quarters_from(first: tuple[int, int]):
    """Yield (year, quarter) from `first` onward, without end."""
    year, quarter = first
    while True:
        yield year, quarter
        year, quarter = (year, quarter + 1) if quarter < 4 else (year + 1, 1)


def download_quarters(dest_dir: Path, *, force: bool = False) -> list[Path]:
    """Download every quarterly ZIP from the first configured quarter until the first 404."""
    agent = config.sec_user_agent()
    zips = []
    for year, quarter in quarters_from(config.FORMD_FIRST_QUARTER):
        dest = dest_dir / "zips" / f"{year}q{quarter}_d.zip"
        urls = [u.format(year=year, quarter=quarter) for u in config.FORMD_URLS]
        if not any(download(url, dest, user_agent=agent, force=force) for url in urls):
            break
        zips.append(dest)
    return zips


def read_table(zip_path: Path, table: str) -> pd.DataFrame:
    """Read one table from a quarterly ZIP as strings. Files sit in a `{YYYY}Q{Q}_d/` folder."""
    with zipfile.ZipFile(zip_path) as archive:
        matches = [n for n in archive.namelist() if Path(n).stem.upper() == table]
        if not matches:
            raise KeyError(f"{table} not found in {zip_path.name}: {archive.namelist()}")
        with archive.open(matches[0]) as handle:
            frame = pd.read_csv(
                handle,
                sep="\t",
                dtype=str,
                keep_default_na=False,
                quoting=3,
                encoding="utf-8",
                encoding_errors="replace",
                on_bad_lines="warn",
            )
    frame.columns = [c.strip().upper() for c in frame.columns]
    frame = frame.apply(lambda col: col.str.strip())
    frame.insert(0, "quarter", zip_path.name.split("_")[0].lower())
    return frame


def parse_date(values: pd.Series) -> pd.Series:
    """Parse the two date formats the SEC uses (30-DEC-2022 and 2022-12-15) to dates."""
    iso = pd.to_datetime(values, format="%Y-%m-%d", errors="coerce")
    sec = pd.to_datetime(values, format="%d-%b-%Y", errors="coerce")
    return iso.fillna(sec).dt.date


def parse_money(values: pd.Series) -> pd.Series:
    """Dollar amounts as floats; "Indefinite" and blanks become NaN."""
    return pd.to_numeric(values.str.replace(",", "", regex=False), errors="coerce")


def build_table(zips: list[Path], table: str) -> pd.DataFrame:
    frame = pd.concat([read_table(z, table) for z in zips], ignore_index=True)
    for column in DATE_COLUMNS.get(table, []):
        frame[column] = parse_date(frame[column])
    for column in MONEY_COLUMNS.get(table, []):
        frame[column] = parse_money(frame[column])
    return frame


def run(dest_dir: Path, zips: list[Path]) -> dict[str, pd.DataFrame]:
    """Parse `zips` into one parquet file per table under `dest_dir`."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    tables = {}
    for table in config.FORMD_TABLES:
        frame = build_table(zips, table)
        frame.to_parquet(dest_dir / f"{table.lower()}.parquet", index=False)
        tables[table] = frame
    return tables


def print_summary(zips: list[Path], tables: dict[str, pd.DataFrame]) -> None:
    names = [z.name.split("_")[0] for z in zips]
    print(f"Quarters downloaded: {len(zips)} ({names[0]} to {names[-1]})")
    for table, frame in tables.items():
        print(f"{table}: {len(frame):,} rows")
    dates = tables["FORMDSUBMISSION"]["FILING_DATE"].dropna()
    print(f"Filing dates: {dates.min()} to {dates.max()}")
    for table, frame in tables.items():
        print(f"\n{table} columns: {', '.join(frame.columns)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="download again even if cached")
    args = parser.parse_args()

    zips = download_quarters(config.FORMD_DIR, force=args.force)
    if not zips:
        raise SystemExit("No Form D quarters could be downloaded.")
    tables = run(config.FORMD_DIR, zips)
    print_summary(zips, tables)

    download(config.ZCTA_COUNTY_URL, config.ZCTA_COUNTY_FILE, force=args.force)
    print(f"\nCensus ZCTA-county file: {config.ZCTA_COUNTY_FILE}")


if __name__ == "__main__":
    main()
