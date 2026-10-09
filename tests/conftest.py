"""Shared fixtures: a dbt build over the synthetic raw files."""

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
