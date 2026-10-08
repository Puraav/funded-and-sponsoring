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
