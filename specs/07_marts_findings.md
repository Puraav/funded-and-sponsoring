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

## Notes from build
- **Listed companies had to go.** The first run counted Intel (1,927 H-1B filings in a year), Synopsys and about 80 other listed companies as "startups", because listed companies file Form D for private placements. `int_bay_area_raises` now drops any filing whose issuer has an SEC industry (SIC) code: only SEC registrants have one, and it is as of the filing quarter, so a company that listed later (Figma) is still counted for the raise it made while private. This removed 146 raises by 80 companies.
- **`not_startups` seed.** Two long-established private firms that file Form D for employee share sales pass every automatic filter and are excluded by hand: DPR Construction and Gensler. They were spotted because of their large H-1B counts, so removing them lowers the rates very slightly; the list is public and has a reason per row.
- After both changes: **2,064 raises by 1,614 startups**; 504 startups (31%) matched; 6,102 Bay Area H-1B filings.
- The "after" window is the filing date plus 12 months, inclusive. "Before" is the 24 months up to the day before filing.
- **The "before" window is short for early raises.** LCA data starts in October 2022, so a raise filed in October 2023 has 12 months of history, not 24. Raises from October 2024 on have the full 24.
- **The rates are a floor.** A startup that sponsors under a name the matcher cannot link counts as not filing.
- A company that raises twice is two rows in `fct_raises`. Role and wage figures use `int_post_raise_lcas`, where each H-1B filing is counted once even if two raises precede it.
- `mart_sponsor_rate` has two rows (`any`, `new_hire`). `mart_roles_wages` has role-group totals as `wage_level = 'All'`. `mart_time_to_lca` is one row per bucket with the median and quartiles repeated.
- `mart_market_share` counts distinct Bay Area employers by normalised name, and also reports the share of filings.
- The known-rates check is a pytest (`tests/test_dbt_fixture.py::test_known_rates`) rather than a dbt singular test, because a dbt test with hard-coded fixture values would fail on the real data. The fixture rates were worked out by hand.
- `findings.py` leaves a finding out when its mart rows are missing (for example no $50M+ raises) instead of printing a blank.
- `docs/lineage.png` is a real screenshot of the dbt docs graph, taken by `web/scripts/lineage-screenshot.mjs` (Playwright).
- Real findings on 2026-10-09: 24% of raises followed by an H-1B filing within a year (n = 1,230); 60% for $50M+ (n = 109) against 6.1% under $2M (n = 328); 64% for startups that had filed before (n = 259) against 13% (n = 971); software is 52% of post-raise filings at a median $179,982; 45% of filing startups filed for an early-career tech role (n = 240); median 98 days to first filing (n = 292); startups are 4.6% of Bay Area H-1B employers and 2.1% of filings.
- dbt project size: 24 models, 9 seeds, 159 build steps including tests.
