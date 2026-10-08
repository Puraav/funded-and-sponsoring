"""fetch_lca converts DOL Excel files (synthetic fixture, real 96-column header)."""

from datetime import date, datetime
from pathlib import Path

import duckdb
import pandas as pd
import pytest

from fundsponsor import fetch_lca

XLSX_DIR = Path(__file__).parent / "fixtures" / "lca_xlsx"
FILES = [
    (XLSX_DIR / "LCA_Disclosure_Data_FY2024_Q2.xlsx", 2024, 2),
    (XLSX_DIR / "LCA_Disclosure_Data_FY2024_Q3.xlsx", 2024, 3),
]


@pytest.fixture(scope="module")
def lca(tmp_path_factory):
    out = tmp_path_factory.mktemp("lca")
    jobs = [(xlsx, out / "parts" / f"{xlsx.stem}.parquet", fy, q) for xlsx, fy, q in FILES]
    fetch_lca.run(jobs, out / "lca_all.parquet")
    return duckdb.sql(f"select * from '{out / 'lca_all.parquet'}'").df().set_index("CASE_NUMBER")


def test_fixture_has_the_real_header():
    header = fetch_lca.read_header(FILES[0][0])
    assert len(header) == 96
    assert not [c for c in fetch_lca.KEEP_COLUMNS if c not in header]


def test_keeps_only_the_spec_columns(lca):
    assert list(lca.reset_index().columns) == [
        *fetch_lca.KEEP_COLUMNS, "fiscal_year", "fiscal_quarter", "source_file",
    ]  # fmt: skip


def test_dedupes_on_case_number_keeping_the_latest_file(lca):
    assert len(lca) == 26  # 20 + 7 rows, one case in both files
    repeated = lca.loc["I-200-24085-000020"]
    assert repeated["CASE_STATUS"] == "Certified - Withdrawn"
    assert repeated["source_file"] == "LCA_Disclosure_Data_FY2024_Q3.xlsx"


def test_excel_text_wrappers_are_removed(lca):
    row = lca.loc["I-200-23300-000002"]
    assert row["JOB_TITLE"] == "Software Engineer I"
    assert row["SOC_CODE"] == "15-1252.00"
    assert row["EMPLOYER_POSTAL_CODE"] == "94107"
    assert pd.isna(row["TRADE_NAME_DBA"])  # ="" is empty
    assert lca.loc["I-200-24079-000009", "TRADE_NAME_DBA"] == "Thistle"


def test_types(lca):
    row = lca.loc["I-200-24030-000006"]
    assert row["RECEIVED_DATE"].date() == date(2024, 2, 1)
    assert row["WAGE_RATE_OF_PAY_FROM"] == 82.5
    assert row["WAGE_UNIT_OF_PAY"] == "Hour"
    assert row["NEW_EMPLOYMENT"] == 1


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('="07310"', "07310"),
        ('=""', None),
        ("  Acme  ", "Acme"),
        (94107, "94107"),
        (94107.0, "94107"),
        (None, None),
    ],
)
def test_clean_text(raw, expected):
    assert fetch_lca.clean_text(raw) == expected


def test_clean_date_and_number():
    assert fetch_lca.clean_date(datetime(2024, 3, 1, 0, 0)) == date(2024, 3, 1)
    assert fetch_lca.clean_date("03/01/2024") == date(2024, 3, 1)
    assert fetch_lca.clean_date("not a date") is None
    assert fetch_lca.clean_number("$1,650.50") == 1650.5
    assert fetch_lca.clean_number("n/a") is None
