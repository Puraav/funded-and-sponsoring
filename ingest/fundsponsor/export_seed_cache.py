"""Copy two small marts to data/seed_cache/*.parquet for the weekly radar.

The full LCA data is too big for GitHub Actions, so the radar models read these committed
extracts instead: H-1B filings per California employer per month, and the CIKs of listed
companies. Re-run this after `dbt build` whenever the LCA or Form D data is refreshed.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

from . import config

EXTRACTS = {
    "lca_employer_history": "mart_lca_employer_history",
    "listed_ciks": "mart_listed_ciks",
}
ORDER = {
    "lca_employer_history": "employer_name, employer_zip5, trade_name_dba, month",
    "listed_ciks": "cik",
}


def export(warehouse: duckdb.DuckDBPyConnection, out_dir: Path) -> dict[str, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name, table in EXTRACTS.items():
        dest = out_dir / f"{name}.parquet"
        # sorted, so the committed file only changes when the data does
        warehouse.execute(
            f"copy (select * from {table} order by {ORDER[name]}) "
            f"to '{dest.as_posix()}' (format parquet, compression zstd)"
        )
        counts[name] = warehouse.execute(f"select count(*) from {table}").fetchone()[0]
    return counts


def main() -> None:
    with duckdb.connect(str(config.WAREHOUSE), read_only=True) as warehouse:
        counts = export(warehouse, config.SEED_CACHE_DIR)
    for name, rows in counts.items():
        path = config.SEED_CACHE_DIR / f"{name}.parquet"
        print(f"{path.relative_to(config.ROOT)}: {rows:,} rows, {path.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
