# Spec 02 — Fetch SEC Form D data

## Source
SEC **Form D Data Sets**, quarterly ZIPs, Sept 2009 onward:
- Page: https://www.sec.gov/data-research/sec-markets-data/form-d-data-sets
- File pattern: `https://www.sec.gov/files/structureddata/data/form-d-data-sets/{YYYY}q{Q}_d.zip` (e.g. `2025q4_d.zip`)
- Field definitions: https://www.sec.gov/files/Form_D.pdf
- Each ZIP holds tab-delimited files: `FORMDSUBMISSION`, `ISSUERS`, `OFFERING`, `RECIPIENTS`, `RELATEDPERSONS`, `SIGNATURES`.

## Build `fetch_formd.py`
1. Download every quarter from **2022 Q4 to the latest published quarter** (probe forward until a 404). Send the SEC User-Agent header; ≤5 requests/second; retry 3× with backoff; skip files that already exist unless `--force`.
2. Extract only `FORMDSUBMISSION`, `ISSUERS`, `OFFERING`, `RELATEDPERSONS`. Concatenate across quarters, add a `quarter` column, save each as parquet in `data/raw/formd/`.
3. Read everything as strings first; parse dates (`FILING_DATE`, `SALE_DATE`) and money (`TOTALOFFERINGAMOUNT`, `TOTALAMOUNTSOLD`; "Indefinite" → NaN) explicitly.
4. Print: quarters downloaded, rows per table, filing-date range, and the column list of each table.

## Also fetch (for Bay Area ZIPs)
Census 2020 ZCTA–county relationship file (same one used in the EV project); spec 04 turns it into a dbt seed:
`https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt` → `data/raw/zcta_county_rel.txt`.

## Done when
- Parquet files exist for the four tables; summary printed
- Column names checked against Form_D.pdf; any differences noted under "Notes from build" below
- Unit test on a tiny synthetic ZIP in `tests/fixtures/` (same file names and tab format)
- Commit `step 02: fetch Form D`

## Notes from build
- **URL moved.** Quarters up to 2026 Q1 are under `/files/structureddata/data/form-d-data-sets/`; 2026 Q2 onward are under `/files/datastandardsinnovation/data/form-d-data-sets/`. `config.FORMD_URLS` lists both and each quarter is tried at each. Without this the probe stops at 2026 Q1 and silently loses six months.
- **Files are `.tsv` inside a folder**, e.g. `2022Q4_d/ISSUERS.tsv`, not bare `ISSUERS`. Tables are found by file stem.
- **Two date formats:** `FILING_DATE` is `30-DEC-2022`, `SALE_DATE` is `2022-12-15`. Both are parsed.
- **Key column is `ACCESSIONNUMBER`** (no underscore). `SUBMISSIONTYPE`, `INDUSTRYGROUPTYPE`, `ENTITYNAME`, `ZIPCODE`, `IS_PRIMARYISSUER_FLAG` (`YES`/`NO`) are as expected.
- Column names were checked against the `FormD_metadata.json` shipped inside each ZIP (same content as Form_D.pdf). Three real columns are not described there: `SCHEMAVERSION`, `TESTORLIVE`, `YEAROFINC_VALUE_ENTERED`. None are used downstream.
- Real run on 2026-10-08: 16 quarters (2022 Q4 to 2026 Q3), 226,125 submissions (one offering each), 230,855 issuers, 783,245 related persons, filing dates 2022-10-03 to 2026-09-30. Every filing has a `FILING_DATE` and a `TOTALAMOUNTSOLD`; `TOTALOFFERINGAMOUNT` is "Indefinite" on roughly half, and `SALE_DATE` is blank where the first sale is yet to occur.
- Fixtures: `tests/make_fixtures.py` writes two synthetic quarterly ZIPs to `tests/fixtures/formd_zips/`. Every company in them is invented.
