"""Every module in the package imports cleanly."""

import importlib

import pytest

MODULES = [
    "config",
    "fetch_formd",
    "fetch_lca",
    "fetch_edgar_recent",
    "make_seeds",
    "match_sample",
    "export_site",
    "findings",
    "charts",
]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    module = importlib.import_module(f"fundsponsor.{name}")
    assert module.__doc__


def test_bay_area_has_nine_counties():
    from fundsponsor import config

    assert len(config.BAY_AREA_COUNTIES) == 9
    assert config.WAREHOUSE.name == "warehouse.duckdb"


def test_missing_user_agent_is_a_clear_error(monkeypatch):
    from fundsponsor import config

    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    with pytest.raises(RuntimeError, match="SEC_USER_AGENT"):
        config.sec_user_agent()
