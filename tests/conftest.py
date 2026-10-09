"""Shared fixtures: a dbt build over the synthetic raw files."""

import duckdb
import pytest

from dbt_helpers import build_fixture_warehouse


@pytest.fixture(scope="session")
def warehouse(tmp_path_factory):
    """A throwaway DuckDB file holding a full dbt build over tests/fixtures/raw."""
    folder = tmp_path_factory.mktemp("dbt")
    path = folder / "fixture.duckdb"
    build_fixture_warehouse(path, folder / "seed_cache")
    with duckdb.connect(str(path), read_only=True) as connection:
        yield connection
