"""Run the dbt project on the synthetic fixtures, the same way for tests and fixture files."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DBT = Path(sys.executable).parent / "dbt"


def build_fixture_warehouse(warehouse: Path, seed_cache: Path) -> None:
    """Build everything into `warehouse`, writing the radar's extracts to `seed_cache`.

    Three steps, because the radar models read the extracts as files: build the main models,
    export the extracts, then build the radar.
    """
    from fundsponsor import export_seed_cache

    env = {
        **os.environ,
        "FS_DATA_DIR": str(ROOT / "tests" / "fixtures" / "raw"),
        "FS_WAREHOUSE": str(warehouse),
        "FS_SEED_CACHE": str(seed_cache),
        "DBT_PROFILES_DIR": str(ROOT / "dbt"),
    }
    target = ["--target-path", str(warehouse.parent / "target")]

    def dbt(*command: str) -> None:
        result = subprocess.run(
            [str(DBT), *command], cwd=ROOT / "dbt", env=env, capture_output=True, text=True
        )
        assert result.returncode == 0, result.stdout[-4000:]

    dbt("deps")
    dbt("build", "--exclude", "tag:radar", *target)
    with duckdb.connect(str(warehouse), read_only=True) as connection:
        export_seed_cache.export(connection, seed_cache)
    dbt("build", "--select", "tag:radar", *target)
