"""Turn the dbt marts into findings.json and the README findings block.

Every number comes from a mart in the DuckDB warehouse; nothing is typed in by hand. Each
finding is a plain-English sentence plus the numbers behind it and its sample size `n`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import duckdb

from . import config

FINDINGS_JSON = config.DATA_DIR / "findings.json"
README = config.ROOT / "README.md"
START, END = "<!-- FINDINGS:START -->", "<!-- FINDINGS:END -->"


def pct(value: float) -> str:
    """0.2374 → '24%'; values under 10% keep one decimal ('6.1%')."""
    return f"{value:.0%}" if value >= 0.0995 else f"{value:.1%}"


def usd(value: float) -> str:
    return f"${value:,.0f}"


def rows(warehouse: duckdb.DuckDBPyConnection, sql: str) -> list[dict]:
    cursor = warehouse.execute(sql)
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]


def build(warehouse: duckdb.DuckDBPyConnection) -> dict:
    """Read the marts and return the findings document."""
    headline = {r["metric"]: r for r in rows(warehouse, "select * from mart_sponsor_rate")}
    rounds = {r["round_bin"]: r for r in rows(warehouse, "select * from mart_by_round")}
    history = {r["history"]: r for r in rows(warehouse, "select * from mart_by_history")}
    roles = rows(
        warehouse, "select * from mart_roles_wages where wage_level = 'All' order by n desc"
    )
    entry = rows(warehouse, "select * from mart_entry_level")[0]
    timing = rows(warehouse, "select * from mart_time_to_lca order by bucket_order")
    market = rows(warehouse, "select * from mart_market_share")[0]
    quality_rows = rows(warehouse, "select * from mart_match_quality")
    quality = {(r["scope"], r["match_rule"]): r for r in quality_rows}
    coverage = rows(
        warehouse,
        """select
               (select count(*) from fct_raises) as raises,
               (select count(*) from dim_company) as companies,
               (select min(filing_date) from fct_raises) as first_raise,
               (select max(filing_date) from fct_raises) as last_raise,
               (select max(filing_date) from fct_raises where has_full_followup) as last_judged,
               (select max(event_date) from int_lca_h1b) as lca_through""",
    )[0]

    any_, new_hire = headline["any"], headline["new_hire"]
    findings = [
        {
            "id": "sponsor_rate",
            "text": (
                f"{pct(any_['sponsor_rate'])} of Bay Area startup raises were followed by at "
                f"least one H-1B filing from the same company within a year "
                f"(n = {any_['n']:,} raises). Counting only filings for new hires, not "
                f"extensions, it is {pct(new_hire['sponsor_rate'])}."
            ),
            "numbers": {
                "sponsor_rate": any_["sponsor_rate"],
                "sponsored": any_["sponsored"],
                "new_hire_rate": new_hire["sponsor_rate"],
                "new_hire_sponsored": new_hire["sponsored"],
            },
            "n": any_["n"],
            "small_sample": any_["small_sample"],
        }
    ]

    big, small = rounds.get("$50M+"), rounds.get("<$2M")
    if big and small:
        middle = [rounds[b] for b in ("$2–10M", "$10–50M") if b in rounds]
        middle_text = "".join(
            f" {r['round_bin']}: {pct(r['sponsor_rate'])} (n = {r['n']:,})." for r in middle
        )
        findings.append(
            {
                "id": "by_round",
                "text": (
                    f"Bigger raises file far more often: {pct(big['sponsor_rate'])} of raises of "
                    f"$50M or more were followed by an H-1B filing (n = {big['n']:,}), against "
                    f"{pct(small['sponsor_rate'])} of raises under $2M (n = {small['n']:,})."
                    f"{middle_text}"
                ),
                "numbers": {
                    r["round_bin"]: {
                        "sponsor_rate": r["sponsor_rate"],
                        "n": r["n"],
                        "median_lcas_per_sponsor": r["median_lcas_per_sponsor"],
                    }
                    for r in sorted(rounds.values(), key=lambda r: r["round_order"])
                },
                "n": sum(r["n"] for r in rounds.values()),
                "small_sample": big["small_sample"] or small["small_sample"],
            }
        )

    before, never = history.get("sponsored_before"), history.get("no_prior")
    if before and never:
        findings.append(
            {
                "id": "by_history",
                "text": (
                    f"Past behaviour is the strongest signal: startups that had filed for H-1B "
                    f"workers in the two years before raising filed again within a year "
                    f"{pct(before['sponsor_rate'])} of the time (n = {before['n']:,}); those "
                    f"with no earlier filing did so {pct(never['sponsor_rate'])} of the time "
                    f"(n = {never['n']:,})."
                ),
                "numbers": {
                    "sponsored_before_rate": before["sponsor_rate"],
                    "sponsored_before_n": before["n"],
                    "no_prior_rate": never["sponsor_rate"],
                    "no_prior_n": never["n"],
                },
                "n": before["n"] + never["n"],
                "small_sample": before["small_sample"] or never["small_sample"],
            }
        )

    total_lcas = sum(r["n"] for r in roles)
    top = roles[0]
    findings.append(
        {
            "id": "roles_wages",
            "text": (
                f"{top['role_group']} roles are {pct(top['share_of_lcas'])} of the H-1B filings "
                f"startups make in the year after raising, at a median offered wage of "
                f"{usd(top['median_wage'])} (n = {top['n']:,} of {total_lcas:,} filings)."
            ),
            "numbers": {
                r["role_group"]: {
                    "n": r["n"],
                    "share": r["share_of_lcas"],
                    "median_wage": r["median_wage"],
                }
                for r in roles
            },
            "n": total_lcas,
            "small_sample": top["small_sample"],
        }
    )

    findings.append(
        {
            "id": "entry_level",
            "text": (
                f"{pct(entry['entry_level_share'])} of the startups that filed after raising "
                f"filed for at least one early-career tech role: a software, data or product "
                f"job at prevailing wage Level I or II (n = {entry['n']:,} startups)."
            ),
            "numbers": {
                "entry_level_share": entry["entry_level_share"],
                "with_entry_level": entry["with_entry_level"],
            },
            "n": entry["n"],
            "small_sample": entry["small_sample"],
        }
    )

    first = timing[0]
    findings.append(
        {
            "id": "time_to_lca",
            "text": (
                f"When a raise is followed by an H-1B filing, the first one comes a median of "
                f"{first['median_days']:.0f} days after the Form D, and a quarter come within "
                f"{first['p25_days']:.0f} days (n = {first['n']:,} raises)."
            ),
            "numbers": {
                "median_days": first["median_days"],
                "p25_days": first["p25_days"],
                "p75_days": first["p75_days"],
                "buckets": {r["bucket"]: r["raises"] for r in timing},
            },
            "n": first["n"],
            "small_sample": first["small_sample"],
        }
    )

    findings.append(
        {
            "id": "market_share",
            "text": (
                f"These startups are a small slice of Bay Area sponsorship: "
                f"{pct(market['employer_share'])} of the region's H-1B employers and "
                f"{pct(market['lca_share'])} of its filings (n = {market['n']:,} employers, "
                f"{market['lcas']:,} filings)."
            ),
            "numbers": {
                "employer_share": market["employer_share"],
                "startup_employers": market["startup_employers"],
                "lca_share": market["lca_share"],
                "startup_lcas": market["startup_lcas"],
                "lcas": market["lcas"],
            },
            "n": market["n"],
            "small_sample": market["small_sample"],
        }
    )

    overall = quality[("overall", None)]
    match_quality = {
        "text": (
            f"Match quality: {overall['startups']:,} of {overall['all_startups']:,} startups "
            f"({pct(overall['match_rate'])}) were matched to an H-1B employer. In a checked "
            f"sample, {overall['labelled_correct']} of {overall['labelled']} matches were "
            f"correct. An unmatched startup counts as not filing, so the rates above are a floor."
        ),
        "startups": overall["all_startups"],
        "matched": overall["startups"],
        "match_rate": overall["match_rate"],
        "labelled": overall["labelled"],
        "labelled_correct": overall["labelled_correct"],
        "precision": overall["match_precision"],
        "by_rule": [
            {
                "rule": r["match_rule"],
                "name": r["rule_name"],
                "tier": r["tier"],
                "pairs": r["pairs"],
                "startups": r["startups"],
                "labelled": r["labelled"],
                "labelled_correct": r["labelled_correct"],
                "precision": r["match_precision"],
                "small_sample": r["small_sample"],
            }
            for (scope, _), r in sorted(quality.items(), key=lambda item: item[0][1] or 0)
            if scope == "rule"
        ],
    }

    return {
        "question": (
            "Of the Bay Area startups that raise money, how many file for H-1B workers within "
            "a year, for which roles, and at what pay?"
        ),
        "coverage": {
            "raises": coverage["raises"],
            "companies": coverage["companies"],
            "first_raise": str(coverage["first_raise"]),
            "last_raise": str(coverage["last_raise"]),
            "last_raise_with_full_followup": str(coverage["last_judged"]),
            "lca_data_through": str(coverage["lca_through"]),
        },
        "findings": findings,
        "match_quality": match_quality,
    }


def readme_block(document: dict) -> str:
    cover = document["coverage"]
    lines = [f"{i}. {finding['text']}" for i, finding in enumerate(document["findings"], 1)]
    lines += [
        "",
        f"_{document['match_quality']['text']}_",
        "",
        f"_Based on {cover['raises']:,} raises by {cover['companies']:,} startups filed from "
        f"{cover['first_raise']} to {cover['last_raise']}. Rates use raises up to "
        f"{cover['last_raise_with_full_followup']}, the last with a full year of LCA data after "
        f"them (the data runs to {cover['lca_data_through']}). An LCA is an application step "
        f"before an H-1B petition, not an approved visa or a hire._",
    ]
    return "\n".join(lines)


def write_readme(document: dict, readme: Path = README) -> None:
    """Replace the text between the FINDINGS markers; add the markers if they are missing."""
    block = f"{START}\n{readme_block(document)}\n{END}"
    text = readme.read_text() if readme.exists() else ""
    if START in text and END in text:
        text = re.sub(f"{re.escape(START)}.*?{re.escape(END)}", lambda _: block, text, flags=re.S)
    else:
        text = text.rstrip() + f"\n\n## Headline findings\n\n{block}\n"
    readme.write_text(text)


def main() -> None:
    with duckdb.connect(str(config.WAREHOUSE), read_only=True) as warehouse:
        document = build(warehouse)
    FINDINGS_JSON.write_text(json.dumps(document, indent=2, default=float) + "\n")
    write_readme(document)
    for i, finding in enumerate(document["findings"], 1):
        flag = "  [small sample]" if finding["small_sample"] else ""
        print(f"{i}. {finding['text']}{flag}\n")
    print(document["match_quality"]["text"])
    print(f"\nWrote {FINDINGS_JSON.relative_to(config.ROOT)} and the findings block in README.md")


if __name__ == "__main__":
    main()
