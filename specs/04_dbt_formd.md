# Spec 04 — dbt: Form D staging and Bay Area startup raises

## Seeds (generated or hand-written, committed)
- `bay_area_zips.csv` — built by `python -m fundsponsor.make_seeds` from the Census ZCTA–county file: `zip, county_fips, county_name` (largest land overlap wins, 9 counties only).
- `fund_name_patterns.csv` — `pattern, reason` regexes for funds/SPVs: `\bfund\b`, `\blp\b`, `\bl\.p\.`, `capital partners`, `ventures? (fund|partners)`, `holdings? lp`, `\bspv\b`, `series [a-z0-9]+ of`, `\breit\b`.
- `excluded_industry_groups.csv` — Pooled Investment Fund, REITS and Finance, Investing, Other Banking and Financial Services, Commercial Banking, Insurance, Residential, Commercial, Other Real Estate.

## Sources
`models/staging/_sources.yml`: dbt-duckdb external sources on the parquet files from spec 02 (`{{ var('raw_dir') }}/formd/*.parquet`).

## Models
1. `stg_formd_submissions`, `stg_formd_issuers`, `stg_formd_offerings`, `stg_formd_people` — rename to snake_case, cast types (dates, decimals; "Indefinite" → null), trim strings, `zip5 = left(zipcode, 5)`.
2. `int_bay_area_raises` (one row per raise):
   - submissions × primary issuer × offering on `accession_number`
   - `submission_type = 'D'` only
   - industry not in `excluded_industry_groups`; name not matching any `fund_name_patterns` (`regexp_matches(lower(name), pattern)`)
   - `zip5` joins `bay_area_zips`
   - `filing_date >= '2023-10-01'`
   - columns: `accession, cik, company, street, city, zip5, county_name, industry, filing_date, first_sale_date, amount_sold, amount_offered, round_bin, is_first_raise`
   - `round_bin`: `<$2M`, `$2–10M`, `$10–50M`, `$50M+`, `unknown`; `is_first_raise` via window over `cik`.
3. `dim_company` (one row per `cik`): latest name, city, county, first/latest raise date, raise count, total sold, and `company_slug` (lowercase, hyphenated, unique; append a short CIK suffix on clashes).

## Tests (`.yml` + singular)
- `unique`/`not_null` on `accession` and `cik` keys; `accepted_values` on `round_bin`; `relationships` raises → dim_company
- singular test: no row in `int_bay_area_raises` matches a fund pattern
- fixture: extend `tests/fixtures/raw/formd/` so CI covers amendment dropped, fund dropped, non-Bay-Area dropped

## Done when
- `dbt build --select +int_bay_area_raises+` green on real data
- Print (via `dbt show` or a small script): raises per quarter, by county, by round bin, top 20 industries, and 15 random rows. **Pause so the user can check they look like startups, not funds.**
- Commit `step 04: dbt Form D models`
