"""Export the dbt marts to web/public/data/*.json for the site.

Only reads finished mart tables and writes JSON; no numbers are computed here.
"""

from __future__ import annotations

import datetime
import decimal
import json
import math
import shutil
from pathlib import Path

import duckdb

from . import config, findings

METRIC_MARTS = [
    "mart_sponsor_rate", "mart_by_round", "mart_by_history", "mart_by_industry",
    "mart_roles_wages", "mart_entry_level", "mart_time_to_lca", "mart_market_share",
]  # fmt: skip
ORDER_BY = {
    "mart_by_round": "round_order",
    "mart_by_history": "history desc",
    "mart_by_industry": "n desc",
    "mart_roles_wages": "role_group, wage_level",
    "mart_time_to_lca": "bucket_order",
    "mart_sponsor_rate": "metric",
}


def clean(value):
    """Make a DuckDB value safe for JSON."""
    if isinstance(value, datetime.date | datetime.datetime):
        return value.isoformat()[:10]
    if isinstance(value, decimal.Decimal):
        value = float(value)
    if isinstance(value, float):
        if math.isnan(value):
            return None
        return int(value) if value.is_integer() else round(value, 4)
    return value


def rows(warehouse: duckdb.DuckDBPyConnection, sql: str, params: list | None = None):
    cursor = warehouse.execute(sql, params or [])
    names = [column[0] for column in cursor.description]
    return [{name: clean(value) for name, value in zip(names, row, strict=True)}
            for row in cursor.fetchall()]  # fmt: skip


def write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "\n")


def group_by_cik(items: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for item in items:
        grouped.setdefault(item.pop("cik"), []).append(item)
    return grouped


def export(warehouse: duckdb.DuckDBPyConnection, out_dir: Path) -> None:
    document = findings.build(warehouse)
    write(out_dir / "findings.json", document)
    write(out_dir / "match_quality.json", document["match_quality"])
    write(
        out_dir / "metrics.json",
        {
            mart: rows(warehouse, f"select * from {mart} order by {ORDER_BY.get(mart, '1')}")
            for mart in METRIC_MARTS
        },
    )

    companies = rows(
        warehouse,
        """select company_slug as slug, company as name, city, county_name as county, industry,
                  latest_raise_date as latest_raise, raise_count as raises, total_sold,
                  round_bin, prior_24m, after_12m, sponsored_before, has_full_followup,
                  lcas_total, median_wage, role_groups, has_page
           from mart_companies
           order by latest_raise_date desc, company""",
    )
    write(out_dir / "companies.json", companies)

    profiles = rows(
        warehouse,
        """select cik, company_slug as slug, company as name, city, county_name as county,
                  industry, first_raise_date as first_raise, latest_raise_date as latest_raise,
                  raise_count as raises, total_sold, lcas_total, median_wage, first_lca_date,
                  latest_lca_date
           from mart_companies where has_page""",
    )
    raises = group_by_cik(rows(
        warehouse,
        """select cik, accession, filing_date, first_sale_date, amount_sold, amount_offered,
                  round_bin, prior_24m, after_12m, has_full_followup
           from fct_raises where cik in (select cik from mart_companies where has_page)
           order by filing_date""",
    ))  # fmt: skip
    monthly = group_by_cik(rows(
        warehouse,
        "select cik, month, lcas, new_hire_lcas from mart_company_monthly_lcas order by month",
    ))  # fmt: skip
    roles = group_by_cik(rows(
        warehouse,
        """select cik, role_group, lcas, early_career_lcas, median_wage, min_wage, max_wage
           from mart_company_roles order by lcas desc""",
    ))  # fmt: skip
    officers = group_by_cik(rows(
        warehouse,
        """select cik, person_name as name, relationships
           from mart_company_officers order by person_seq""",
    ))  # fmt: skip

    company_dir = out_dir / "company"
    shutil.rmtree(company_dir, ignore_errors=True)
    for profile in profiles:
        cik = profile["cik"]
        write(
            company_dir / f"{profile['slug']}.json",
            {
                **profile,
                "raise_list": raises.get(cik, []),
                "monthly_lcas": monthly.get(cik, []),
                "roles": roles.get(cik, []),
                "officers": officers.get(cik, []),
            },
        )

    # the radar arrives in spec 10; until then the site gets an empty list
    if not (out_dir / "radar.json").exists():
        write(out_dir / "radar.json", {"generated": None, "days": None, "rows": []})


def summary(out_dir: Path) -> str:
    files = [p for p in out_dir.rglob("*.json")]
    size = sum(p.stat().st_size for p in files)
    return f"{len(files):,} JSON files, {size / 1e6:.1f} MB in {out_dir}"


def main() -> None:
    with duckdb.connect(str(config.WAREHOUSE), read_only=True) as warehouse:
        export(warehouse, config.WEB_DATA_DIR)
    print(summary(config.WEB_DATA_DIR))
    for name in ("findings.json", "metrics.json", "match_quality.json", "companies.json",
                 "radar.json"):  # fmt: skip
        path = config.WEB_DATA_DIR / name
        print(f"  {name}: {path.stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
