# Spec 05 — dbt: LCA staging and H-1B events

## Seed
`soc_role_groups.csv`: `soc_code, role_group` plus `title_keywords.csv`: `keyword, role_group, priority`.
- `Software`: SOC 15-1252, 15-1253, 15-1254, 15-1255, 15-1256; 15-1299 when the title has engineer/developer
- `Data`: 15-2051, 15-2041, 15-1243, 15-1242; or title has data scientist / data analyst / data engineer / analytics / machine learning
- `Product`: title has product manager / product owner / program manager; or 11-3021 with "product" in the title
- `Other tech`: remaining 15-xxxx · `Non-tech`: everything else
Title keywords win over SOC when they point to Data or Product.

## Models
1. `stg_lca` — from `{{ var('raw_dir') }}/lca/lca_all.parquet`: snake_case, typed dates and numbers, `employer_zip5`, upper-trimmed state.
2. `int_lca_h1b` — `visa_class = 'H-1B'` and `case_status = 'Certified'`; `event_date = coalesce(received_date, decision_date)`; `is_new_hire`; `annual_wage` from `wage_rate_of_pay_from` × unit (Year 1, Month 12, Bi-Weekly 26, Week 52, Hour 2080), set to null outside $20k–$1M; `role_group` from the seeds; `pw_wage_level`.
3. `fct_lca_events` is built in spec 06, after matching.

## Tests
- `not_null` on `case_number`, `event_date`; `unique` on `case_number`
- `accepted_values` on `role_group`
- singular test: median `annual_wage` for Software in CA between $110k and $230k (catches unit bugs)

## Done when
- `dbt build --select +int_lca_h1b` green
- Print rows kept, share new-hire, rows and median wage per role group and per wage level
- Commit `step 05: dbt LCA models`

## Notes from build
- `title_keywords.csv` has a fourth column, `only_soc`. It carries the two conditional rules in the spec ("15-1299 when the title has engineer/developer" → Software; "11-3021 with product in the title" → Product) so that all role logic lives in the seeds.
- Keyword priority, lowest wins: product manager / product owner / program manager (1), "product" on 11-3021 (2), the Data keywords (3), engineer / developer on 15-1299 (4). So "Data Product Manager" is Product, and "Machine Learning Engineer" on a software SOC code is Data.
- `soc_code` in the model is the first seven characters (`15-1252`); the raw value is `15-1252.00`.
- Only `case_status = 'Certified'` counts. "Certified - Withdrawn" (about 6% of rows) is excluded.
- `pw_wage_level` keeps I to IV only; `N/A` and blank become null (about 8% of certified H-1B rows).
- A "Software Engineer" title filed under a non-software SOC code such as 15-1211 lands in "Other tech", as the spec's rules say. About 4,800 rows.
- Real run: **1,877,445 certified H-1B LCAs**, event dates 2022-09-26 to 2026-06-23, 51% new-hire. `annual_wage` is null on 2,338 rows (outside $20k to $1M).

  | role group | rows | median wage |
  |---|---|---|
  | Software | 719,241 | $126,000 |
  | Non-tech | 647,296 | $105,000 |
  | Other tech | 282,557 | $104,520 |
  | Data | 188,011 | $123,092 |
  | Product | 40,340 | $151,819 |

  | wage level | rows | median wage |
  |---|---|---|
  | I | 321,113 | $81,786 |
  | II | 750,708 | $105,000 |
  | III | 368,255 | $134,514 |
  | IV | 294,478 | $160,000 |
  | none | 142,891 | $141,383 |

- Sanity test: median wage for Software roles worked in California is **$170,000** (allowed range $110k to $230k).
