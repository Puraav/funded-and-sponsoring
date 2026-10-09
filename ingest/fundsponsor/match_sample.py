"""Write data/match_sample.csv, a sample of matches for hand-labelling.

60 matched pairs spread over the four matching rules, plus 20 startups with no match (each
shown next to the closest-named California employer, so a missed match can be spotted).
The `correct` column is left empty for a person to fill with y or n.
"""

from __future__ import annotations

import argparse

import duckdb
import pandas as pd

from . import config

SAMPLE = config.DATA_DIR / "match_sample.csv"
MATCHED_TOTAL = 60
UNMATCHED_TOTAL = 20

# Each pair gets a stable pseudo-random rank, so re-running gives the same sample.
MATCHED_SQL = """
with startups as (
    select cik, any_value(street) as street
    from int_bay_area_raises
    group by cik
),
employers as (
    select
        employer_name,
        employer_zip5,
        any_value(trade_name_dba) as trade_name_dba,
        any_value(employer_address1) as employer_address,
        any_value(employer_city) as employer_city,
        any_value(employer_state) as employer_state,
        count(*) as lca_count,
        any_value(job_title) as example_job_title
    from int_lca_h1b
    group by employer_name, employer_zip5
),
ranked as (
    select
        matches.*,
        row_number() over (
            partition by matches.match_rule
            order by hash(matches.cik || matches.employer_name || matches.employer_zip5)
        ) as pick
    from int_matches as matches
),
-- round-robin over the rules: every rule's 1st pick, then every rule's 2nd pick, ...
chosen as (
    select * from ranked order by pick, match_rule limit ?
)
select
    'matched' as sample_type,
    chosen.match_rule,
    chosen.tier,
    chosen.cik,
    companies.company,
    startups.street as company_street,
    companies.city as company_city,
    companies.zip5 as company_zip5,
    employers.employer_name,
    employers.trade_name_dba,
    employers.employer_address,
    employers.employer_city,
    employers.employer_state,
    chosen.employer_zip5,
    employers.lca_count,
    employers.example_job_title,
    '' as correct
from chosen
inner join dim_company as companies using (cik)
inner join startups using (cik)
inner join employers using (employer_name, employer_zip5)
order by chosen.match_rule, companies.company
"""

UNMATCHED_SQL = """
with unmatched as (
    select companies.*
    from dim_company as companies
    where companies.cik not in (select cik from int_matches)
    order by hash(companies.cik)
    limit ?
),
startups as (
    select cik, any_value(street) as street
    from int_bay_area_raises
    group by cik
),
startup_keys as (
    select cik, any_value(name_key) as name_key, any_value(first_token) as first_token
    from int_name_keys
    where source = 'formd'
    group by cik
),
-- the closest-named California employer that shares the startup's first word
nearest as (
    select
        startup_keys.cik,
        arg_max(employers.entity_name, similarity) as employer_name,
        arg_max(employers.zip5, similarity) as employer_zip5
    from startup_keys
    inner join (select * from int_name_keys where source = 'lca' and state = 'CA') as employers
        on startup_keys.first_token = employers.first_token,
    lateral (
        select jaro_winkler_similarity(startup_keys.name_key, employers.name_key) as similarity
    )
    group by startup_keys.cik
),
employers as (
    select
        employer_name,
        employer_zip5,
        any_value(trade_name_dba) as trade_name_dba,
        any_value(employer_address1) as employer_address,
        any_value(employer_city) as employer_city,
        any_value(employer_state) as employer_state,
        count(*) as lca_count,
        any_value(job_title) as example_job_title
    from int_lca_h1b
    group by employer_name, employer_zip5
)
select
    'unmatched' as sample_type,
    null as match_rule,
    null as tier,
    unmatched.cik,
    unmatched.company,
    startups.street as company_street,
    unmatched.city as company_city,
    unmatched.zip5 as company_zip5,
    nearest.employer_name,
    employers.trade_name_dba,
    employers.employer_address,
    employers.employer_city,
    employers.employer_state,
    nearest.employer_zip5,
    employers.lca_count,
    employers.example_job_title,
    '' as correct
from unmatched
inner join startups using (cik)
left join nearest using (cik)
left join employers using (employer_name, employer_zip5)
order by unmatched.company
"""


SEED = config.ROOT / "dbt" / "seeds" / "match_labels.csv"
SEED_COLUMNS = [
    "sample_type", "match_rule", "tier", "cik", "company", "employer_name", "employer_zip5",
    "correct", "confidence", "evidence",
]  # fmt: skip


def write_seed() -> None:
    """Copy the labelled sample into the dbt seed that mart_match_quality reads."""
    labelled = pd.read_csv(SAMPLE, dtype=str).fillna("")
    labelled["correct"] = labelled["correct"].str.strip().str.lower()
    bad = labelled[~labelled["correct"].isin(["y", "n"])]
    if len(bad):
        raise SystemExit(f"{len(bad)} rows in {SAMPLE.name} have no y/n in `correct`.")
    for column in SEED_COLUMNS:
        if column not in labelled:
            labelled[column] = ""
    labelled[SEED_COLUMNS].to_csv(SEED, index=False)
    print(f"Wrote {len(labelled)} labels to {SEED.relative_to(config.ROOT)}")
    print(labelled.groupby(["sample_type", "match_rule", "correct"]).size().to_string())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--to-seed", action="store_true", help="copy the labelled sample to dbt")
    parser.add_argument("--force", action="store_true", help="overwrite a labelled sample")
    args = parser.parse_args()
    if args.to_seed:
        write_seed()
        return
    if SAMPLE.exists() and not args.force:
        existing = pd.read_csv(SAMPLE, dtype=str).fillna("")
        if existing.get("correct", pd.Series(dtype=str)).str.strip().ne("").any():
            raise SystemExit(f"{SAMPLE.name} already has labels. Use --force to replace it.")

    with duckdb.connect(str(config.WAREHOUSE), read_only=True) as warehouse:
        print("Match rate by rule:")
        total = warehouse.sql("select count(*) from dim_company").fetchone()[0]
        for rule, tier, pairs, startups in warehouse.sql(
            """select match_rule, tier, count(*), count(distinct cik)
               from int_matches group by 1, 2 order by 1"""
        ).fetchall():
            print(f"  rule {rule} ({tier}): {pairs} pairs, {startups} startups")
        matched = warehouse.sql("select count(distinct cik) from int_matches").fetchone()[0]
        print(f"  startups matched: {matched} of {total} ({matched / total:.1%})")

        sample = warehouse.execute(MATCHED_SQL, [MATCHED_TOTAL]).df()
        unmatched = warehouse.execute(UNMATCHED_SQL, [UNMATCHED_TOTAL]).df()

    sample = pd.concat([sample, unmatched.astype(object)], ignore_index=True)
    sample["match_rule"] = sample["match_rule"].astype("Int64")
    sample["lca_count"] = sample["lca_count"].astype("Int64")
    sample.to_csv(SAMPLE, index=False)
    print(f"\nWrote {len(sample)} rows to {SAMPLE.relative_to(config.ROOT)}")
    print(sample.groupby(["sample_type", "match_rule"], dropna=False).size().to_string())
    print(
        "\nFill the `correct` column with y or n.\n"
        "  matched rows:   y if the employer is the same company as the startup.\n"
        "  unmatched rows: y if leaving it unmatched is right (the employer shown is a "
        "different company, or none is shown); n if they are the same company."
    )


if __name__ == "__main__":
    main()
