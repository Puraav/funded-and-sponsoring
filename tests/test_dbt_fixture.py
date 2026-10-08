"""Build the dbt project on the synthetic fixtures and check the rules that matter."""

import os
import subprocess
import sys
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]
DBT = Path(sys.executable).parent / "dbt"


@pytest.fixture(scope="session")
def warehouse(tmp_path_factory):
    """A throwaway DuckDB file holding a full `dbt build` over tests/fixtures/raw."""
    path = tmp_path_factory.mktemp("dbt") / "fixture.duckdb"
    env = {
        **os.environ,
        "FS_DATA_DIR": str(ROOT / "tests" / "fixtures" / "raw"),
        "FS_WAREHOUSE": str(path),
        "DBT_PROFILES_DIR": str(ROOT / "dbt"),
    }
    for command in (["deps"], ["build", "--target-path", str(path.parent / "target")]):
        result = subprocess.run(
            [str(DBT), *command], cwd=ROOT / "dbt", env=env, capture_output=True, text=True
        )
        assert result.returncode == 0, result.stdout[-4000:]
    with duckdb.connect(str(path), read_only=True) as connection:
        yield connection


def test_only_bay_area_startup_raises_are_kept(warehouse):
    rows = warehouse.sql(
        "select accession, round_bin, is_first_raise from int_bay_area_raises order by accession"
    ).fetchall()
    # Dropped: amendment, fund (industry and name), Texas company, real estate, LLC under
    # "Other", business combination, and the filing before 2023-10-01.
    assert rows == [
        ("0009000001-23-000001", "$2–10M", True),  # Quillfern, first raise
        ("0009000001-24-000003", "$10–50M", False),  # Quillfern, second raise
        ("0009000004-23-000001", "unknown", True),  # Marrowgate, nothing sold yet
        ("0009000007-24-000001", "<$2M", False),  # Nimbus, raised before the cut-off too
    ]


def test_dim_company_is_one_row_per_company(warehouse):
    rows = warehouse.sql(
        "select company_slug, county_name, raise_count, total_sold from dim_company order by 1"
    ).fetchall()
    assert rows == [
        ("marrowgate-health-corp", "Santa Clara", 1, 0),
        ("nimbus-thistle-ai-inc", "Alameda", 1, 750_000),
        ("quillfern-robotics-inc", "San Francisco", 2, 30_000_000),
    ]


def test_only_certified_h1b_cases_are_events(warehouse):
    cases = {row[0] for row in warehouse.sql("select case_number from int_lca_h1b").fetchall()}
    assert len(cases) == 18
    # Withdrawn, E-3, H-1B1 and certified-then-withdrawn cases are not sponsoring events.
    assert not cases & {
        "I-200-24040-000007",
        "I-203-24041-000008",
        "I-201-24005-000017",
        "I-200-24085-000020",
    }


def test_role_groups_wages_and_new_hire_flag(warehouse):
    rows = {
        case: (role, wage, new_hire)
        for case, role, wage, new_hire in warehouse.sql(
            "select case_number, role_group, annual_wage, is_new_hire from int_lca_h1b"
        ).fetchall()
    }
    assert rows["I-200-23001-000001"] == ("Software", 165_000, True)
    # change of employer counts as a new hire; the title beats the marketing-manager SOC code
    assert rows["I-200-24010-000004"] == ("Product", 205_000, True)
    assert rows["I-200-24020-000005"] == ("Non-tech", 150_000, False)  # an extension
    assert rows["I-200-24030-000006"] == ("Software", 171_600, True)  # $82.50 an hour
    assert rows["I-200-24079-000009"][0] == "Data"  # "Machine Learning" beats a software SOC
    assert rows["I-200-24080-000010"] == ("Other tech", 168_000, True)  # $14,000 a month
    assert rows["I-200-24051-000012"] == ("Data", 80_600, True)  # $3,100 every two weeks
    assert rows["I-200-24004-000016"] == ("Non-tech", 85_800, True)  # $1,650 a week
    assert rows["I-200-24006-000018"][1] is None  # $5M a year is a typo, not a wage
    assert rows["I-200-24100-000021"][0] == "Product"
    assert rows["I-200-24130-000022"][0] == "Data"
