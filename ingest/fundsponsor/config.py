"""Paths, URLs and constants shared by every ingest script."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

# FS_DATA_DIR points the whole pipeline at another raw-data folder (tests and CI use fixtures).
RAW_DIR = Path(os.environ["FS_DATA_DIR"]).resolve() if os.environ.get("FS_DATA_DIR") else (
    ROOT / "data" / "raw"
)
DATA_DIR = ROOT / "data"
CHARTS_DIR = ROOT / "charts"
WAREHOUSE = DATA_DIR / "warehouse.duckdb"
WEB_DATA_DIR = ROOT / "web" / "public" / "data"

# The nine Bay Area counties, keyed by 5-digit county FIPS.
BAY_AREA_COUNTIES = {
    "06001": "Alameda",
    "06013": "Contra Costa",
    "06041": "Marin",
    "06055": "Napa",
    "06075": "San Francisco",
    "06081": "San Mateo",
    "06085": "Santa Clara",
    "06095": "Solano",
    "06097": "Sonoma",
}

SEC_MAX_REQUESTS_PER_SECOND = 5


def sec_user_agent() -> str:
    """Return the declared SEC User-Agent, or fail clearly if it is not set."""
    agent = os.environ.get("SEC_USER_AGENT", "").strip()
    if not agent:
        raise RuntimeError(
            "SEC_USER_AGENT is not set. Copy .env.example to .env and set it to "
            '"Your Name your@email", as the SEC asks of every automated client.'
        )
    return agent
