# Spec 07 — dbt marts, metrics and findings

## `fct_raises` (one row per raise)
Join raises to `fct_lca_events` on `cik`:
- `prior_24m` — LCAs with `event_date` in the 24 months **before** `filing_date`
- `after_12m`, `after_12m_new_hire` — in the 12 months **after**
- `sponsored_after` (boolean), role-group counts after, median annual wage after
- `has_full_followup` = `filing_date <= max(event_date) - interval 365 day`. Only these count in after-rates.

## Metric marts (each with `n`, and `small_sample = n < 30`)
1. `mart_sponsor_rate` — overall share of raises with `sponsored_after`, plus new-hire-only version
2. `mart_by_round` — sponsor rate + median LCAs per sponsoring startup, by `round_bin`
3. `mart_by_history` — sponsor rate when `prior_24m >= 1` vs `= 0`
4. `mart_by_industry` — top 8 industries by count
5. `mart_roles_wages` — post-raise LCAs by role group; median wage by role group × `pw_wage_level`
6. `mart_entry_level` — share of sponsoring startups with ≥1 Level I/II LCA in Software, Data or Product
7. `mart_time_to_lca` — days from Form D filing to first LCA after it: median, quartiles, histogram buckets
8. `mart_market_share` — share of all Bay Area H-1B employers (by distinct employer) that are in our startup set

## Tests
- rates between 0 and 1; `n > 0`; singular test that `mart_by_round` counts sum to `mart_sponsor_rate.n`
- CI fixture: a tiny hand-built dataset where expected rates are known; assert them in a singular test

## Findings (`python -m fundsponsor.findings`)
- Reads the marts from DuckDB → `data/findings.json` with 5–7 plain-English findings, each with its numbers and n, e.g. "X% of Bay Area startups that raised $10–50M filed for at least one H-1B worker within a year (n = Y)."
- Writes them into README between `<!-- FINDINGS:START -->` and `<!-- FINDINGS:END -->`, with the match-quality line.

## Done when
- `dbt build` green; findings printed with every n
- `dbt docs generate` works; save a lineage graph screenshot to `docs/lineage.png`
- Commit `step 07: marts and findings`
