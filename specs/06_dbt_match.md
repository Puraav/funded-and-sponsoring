# Spec 06 — dbt: match startups to H-1B employers (the hard part, in SQL)

Precision beats recall: a wrong match puts a false number in the findings.

## Name keys
Write a dbt macro `normalise_name(col)`: lowercase → remove punctuation → remove legal suffixes as whole words (`inc, incorporated, corp, corporation, co, company, llc, l l c, ltd, limited, pbc, plc, lp`) → remove leading "the" → collapse spaces → trim. Keep words like labs, ai, technologies.
- `int_name_keys`: one row per distinct (source, name, zip5) for both Form D companies and LCA employers (`employer_name` and `trade_name_dba`), with `name_key`, `first_token`, `zip3`, `is_generic` (key is one word of ≤ 5 letters, or appears in a `generic_names` seed you write with ~50 common words like mercury, ramp, nova, atlas, apex).

## `int_matches`: tiers, stop at the first that matches
1. Same `name_key` + same `zip5` → `high`
2. Same `name_key` + employer ZIP in `bay_area_zips` → `high`
3. Same `name_key`, employer in CA → `medium`
4. Fuzzy: DuckDB `jaro_winkler_similarity(a, b) ≥ 0.97` within the same `zip3` and same `first_token` (blocking) → `medium`
Rules:
- `is_generic` names may only match in tier 1.
- If one LCA employer matches more than one CIK, keep the best tier; on a tie, drop both and record them in `int_match_conflicts`.
Output: `cik, company, employer_name, employer_zip5, tier`.

## Validation (required)
1. `python -m fundsponsor.match_sample` writes `data/match_sample.csv`: 60 matched pairs (20 per tier where available) + 20 unmatched startups, with names, addresses, tier, and an empty `correct` column.
2. **Stop and ask the user to label it** (y/n). Then copy it to `dbt/seeds/match_labels.csv` and `dbt seed`.
3. `mart_match_quality`: match rate overall and per tier, precision per tier from the labels, sample sizes.
4. If any tier is below 90% precision, tighten or drop it, re-run, and re-check.

## Then
`fct_lca_events`: `int_lca_h1b` joined to `int_matches` → every certified H-1B LCA with its `cik`.

## Tests
- `unique` on (`cik`, `employer_name`, `employer_zip5`) in `int_matches`
- singular test: every tier kept has precision ≥ 0.90 in `mart_match_quality`
- macro unit test on 15 name cases (dbt unit tests or a singular test over a seed of `raw, expected`)

## Done when
- Match rate by tier printed; sample labelled; precision ≥ 90% per kept tier
- Commit `step 06: entity matching in dbt`

## Notes from build
**Status: built up to the labelling step. Waiting for `data/match_sample.csv` to be labelled; `match_labels`, `mart_match_quality`, `fct_lca_events` and the precision test come after.**

- `normalise_name` removes legal suffixes **only at the end of the name** (repeatedly), not anywhere in it, so "The Browser Company of New York, Inc." keeps "company". It also drops a trailing SEC state tag (`/DE/`, `\DE`), turns `&` into "and", and removes dots and apostrophes without leaving a space (`L.L.C.` → `llc`, `Luke's` → `lukes`). Tested on 16 cases in the `name_cases` seed.
- Two helper models were added: `int_match_candidates` (every pair with the strictest rule it passes) feeds both `int_matches` and `int_match_conflicts`.
- `int_matches` has `match_rule` (1 to 4) as well as `tier`, so precision can be judged per rule: rules 1 and 2 are `high`, 3 and 4 are `medium`.
- LCA employers are keyed on their legal name **and** their trade name, which finds renamed companies: Harvey AI Corp ↔ "Counsel AI Corporation" (dba Harvey AI), FlowFuse ↔ "FlowForge Inc" (dba FlowFuse).
- A startup's key comes from every name and ZIP it used across its raises, so a rule 1 match can be on an earlier address than the one in `dim_company`.
- Real run: **546 of 1,694 startups (32.2%) match at least one H-1B employer**, 785 pairs, 19,805 certified H-1B LCAs.

  | rule | tier | pairs | startups |
  |---|---|---|---|
  | 1 same name, same ZIP | high | 564 | 456 |
  | 2 same name, Bay Area | high | 208 | 177 |
  | 3 same name, California | medium | 12 | 10 |
  | 4 fuzzy, same 3-digit ZIP | medium | 1 | 1 |

- No conflicts on real data (`int_match_conflicts` is empty).
- Known misses, by design: 17 startups whose only same-name employer is outside California (e.g. ConductorOne in Oregon, AtScale in Massachusetts), and 9 startups with short names blocked by the generic rule because the employer is in a different Bay Area ZIP (e.g. AiFi, Lilt, Vooma).
- The sample has 80 rows: 24 from rule 1, 23 from rule 2, all 12 from rule 3, the 1 from rule 4, and 20 unmatched startups. Unmatched rows show the closest-named California employer that shares the startup's first word, when there is one, so a missed match can be seen.
