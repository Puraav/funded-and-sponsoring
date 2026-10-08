"""fetch_formd parses the SEC's quarterly ZIP layout (synthetic fixture, real format)."""

import math
from datetime import date
from pathlib import Path

import pandas as pd

from fundsponsor import config, fetch_formd

ZIPS = sorted((Path(__file__).parent / "fixtures" / "formd_zips").glob("*.zip"))


def test_fixture_zips_exist():
    assert [z.name for z in ZIPS] == ["2023q3_d.zip", "2023q4_d.zip", "2024q1_d.zip"]


def test_run_writes_one_parquet_per_table(tmp_path):
    tables = fetch_formd.run(tmp_path, ZIPS)

    assert set(tables) == set(config.FORMD_TABLES)
    for table in config.FORMD_TABLES:
        assert (tmp_path / f"{table.lower()}.parquet").exists()

    submissions = pd.read_parquet(tmp_path / "formdsubmission.parquet")
    assert len(submissions) == 12
    assert set(submissions["quarter"]) == {"2023q3", "2023q4", "2024q1"}
    assert submissions["ACCESSIONNUMBER"].is_unique
    # 12 primary issuers plus one extra non-primary issuer
    assert len(tables["ISSUERS"]) == 13


def test_dates_parse_from_both_sec_formats(tmp_path):
    tables = fetch_formd.run(tmp_path, ZIPS)
    filed = tables["FORMDSUBMISSION"].set_index("ACCESSIONNUMBER")["FILING_DATE"]
    sale = tables["OFFERING"].set_index("ACCESSIONNUMBER")["SALE_DATE"]

    assert filed["0009000001-23-000001"] == date(2023, 10, 5)  # 05-OCT-2023
    assert sale["0009000001-23-000001"] == date(2023, 9, 28)  # 2023-09-28
    assert pd.isna(sale["0009000004-23-000001"])  # blank sale date


def test_indefinite_amounts_become_nan(tmp_path):
    offering = fetch_formd.run(tmp_path, ZIPS)["OFFERING"].set_index("ACCESSIONNUMBER")

    assert math.isnan(offering.loc["0009000002-23-000001", "TOTALOFFERINGAMOUNT"])
    assert offering.loc["0009000002-23-000001", "TOTALAMOUNTSOLD"] == 12_000_000
    assert offering.loc["0009000004-23-000001", "TOTALAMOUNTSOLD"] == 0


def test_strings_stay_strings(tmp_path):
    issuers = fetch_formd.run(tmp_path, ZIPS)["ISSUERS"].set_index("ACCESSIONNUMBER")
    row = issuers.loc["0009000004-23-000001"]

    assert row["CIK"] == "0009000004"  # leading zeros survive
    assert row["ZIPCODE"] == "94301-1234"


def test_quarters_roll_over_the_year():
    quarters = fetch_formd.quarters_from((2022, 4))
    assert [next(quarters) for _ in range(3)] == [(2022, 4), (2023, 1), (2023, 2)]
