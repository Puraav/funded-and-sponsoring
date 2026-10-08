"""Build the bay_area_zips dbt seed from the Census ZCTA-county relationship file.

A ZIP code area (ZCTA) can straddle counties; each is assigned to the county holding most of
its land area. Only ZCTAs whose main county is one of the nine Bay Area counties are kept.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import config

SEED = config.ROOT / "dbt" / "seeds" / "bay_area_zips.csv"


def bay_area_zips(relationship_file: Path) -> pd.DataFrame:
    frame = pd.read_csv(
        relationship_file,
        sep="|",
        dtype=str,
        encoding="utf-8-sig",
        usecols=["GEOID_ZCTA5_20", "GEOID_COUNTY_20", "AREALAND_PART"],
    ).dropna(subset=["GEOID_ZCTA5_20"])
    frame["AREALAND_PART"] = pd.to_numeric(frame["AREALAND_PART"]).fillna(0)
    main = (
        frame.sort_values(["GEOID_ZCTA5_20", "AREALAND_PART", "GEOID_COUNTY_20"])
        .groupby("GEOID_ZCTA5_20")
        .tail(1)
    )
    main = main[main["GEOID_COUNTY_20"].isin(config.BAY_AREA_COUNTIES)]
    return pd.DataFrame(
        {
            "zip": main["GEOID_ZCTA5_20"],
            "county_fips": main["GEOID_COUNTY_20"],
            "county_name": main["GEOID_COUNTY_20"].map(config.BAY_AREA_COUNTIES),
        }
    ).sort_values("zip")


def main() -> None:
    if not config.ZCTA_COUNTY_FILE.exists():
        raise SystemExit(f"{config.ZCTA_COUNTY_FILE} is missing. Run fetch_formd first.")
    seed = bay_area_zips(config.ZCTA_COUNTY_FILE)
    seed.to_csv(SEED, index=False)
    print(f"Wrote {len(seed)} Bay Area ZIPs to {SEED.relative_to(config.ROOT)}")
    print(seed.groupby("county_name").size().to_string())


if __name__ == "__main__":
    main()
