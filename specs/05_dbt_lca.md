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
