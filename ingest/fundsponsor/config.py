"""Paths, URLs and constants shared by every ingest script."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

# FS_DATA_DIR points the whole pipeline at another raw-data folder (tests and CI use fixtures).
RAW_DIR = (
    Path(os.environ["FS_DATA_DIR"]).resolve()
    if os.environ.get("FS_DATA_DIR")
    else (ROOT / "data" / "raw")
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


# --- SEC Form D quarterly data sets (spec 02) ---
# The SEC moved the folder in 2026: quarters up to 2026 Q1 sit under structureddata/, later
# ones under datastandardsinnovation/. Each quarter is tried at every base in turn.
FORMD_URLS = (
    "https://www.sec.gov/files/structureddata/data/form-d-data-sets/{year}q{quarter}_d.zip",
    "https://www.sec.gov/files/datastandardsinnovation/data/form-d-data-sets/{year}q{quarter}_d.zip",
)
FORMD_FIRST_QUARTER = (2022, 4)
FORMD_TABLES = ("FORMDSUBMISSION", "ISSUERS", "OFFERING", "RELATEDPERSONS")
FORMD_DIR = RAW_DIR / "formd"

ZCTA_COUNTY_URL = (
    "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/"
    "tab20_zcta520_county20_natl.txt"
)
ZCTA_COUNTY_FILE = RAW_DIR / "zcta_county_rel.txt"

# --- DOL LCA disclosure data (spec 03) ---
# Honest, descriptive agent for sites that are not the SEC (DOL rejects browser look-alikes).
PUBLIC_USER_AGENT = "fundsponsor research (github.com/Puraav/funded-and-sponsoring)"

LCA_PAGE = "https://www.dol.gov/agencies/eta/foreign-labor/performance"
_LCA_BASE = "https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs"
# (fiscal year, quarter, url). Since FY2020 each file holds ONE quarter of decisions, not the
# year to date, so every quarter is needed. FY = October to September.
LCA_FILES = [
    (fy, q, f"{_LCA_BASE}/LCA_Disclosure_Data_FY{fy}_Q{q}.xlsx")
    for fy in (2023, 2024, 2025)
    for q in (1, 2, 3, 4)
] + [
    (2026, 3, "https://www.dol.gov/media/LCA_Disclosure_Data_FY2026_Q3.xlsx"),
]
LCA_DIR = RAW_DIR / "lca"
LCA_PARQUET = LCA_DIR / "lca_all.parquet"
