# Spec 03 — Fetch DOL LCA disclosure data

## Source
DOL Office of Foreign Labor Certification **LCA disclosure data** (H-1B, H-1B1, E-3), quarterly cumulative Excel files per fiscal year (FY = Oct–Sep).
- Page: https://www.dol.gov/agencies/eta/foreign-labor/performance (section "Disclosure Data")
- Usual file pattern: `https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/LCA_Disclosure_Data_FY{YYYY}_Q{Q}.xlsx`
- Record layout PDF is linked next to the files on the same page. If the pattern 404s, open the page, find the current links and update `config.py`.

## Which files
- FY2023 Q4, FY2024 Q4, FY2025 Q4 (each Q4 file covers the full fiscal year)
- FY2026: the latest quarter published (Q4 if out, otherwise Q3)
That covers Oct 2022 → latest, enough for "24 months before" and "12 months after" each raise.

## Build `fetch_lca.py`
1. Download each file (they're large, ~100 MB+; stream to disk, show progress, skip if present).
2. Convert each to parquet **once**, keeping only these columns (print the real header first and map if names differ):
   `CASE_NUMBER, CASE_STATUS, RECEIVED_DATE, DECISION_DATE, VISA_CLASS, JOB_TITLE, SOC_CODE, SOC_TITLE, FULL_TIME_POSITION, BEGIN_DATE, TOTAL_WORKER_POSITIONS, NEW_EMPLOYMENT, CONTINUED_EMPLOYMENT, CHANGE_EMPLOYER, EMPLOYER_NAME, TRADE_NAME_DBA, EMPLOYER_ADDRESS1, EMPLOYER_CITY, EMPLOYER_STATE, EMPLOYER_POSTAL_CODE, NAICS_CODE, WORKSITE_CITY, WORKSITE_STATE, WORKSITE_POSTAL_CODE, WAGE_RATE_OF_PAY_FROM, WAGE_RATE_OF_PAY_TO, WAGE_UNIT_OF_PAY, PREVAILING_WAGE, PW_UNIT_OF_PAY, PW_WAGE_LEVEL`
3. De-duplicate on `CASE_NUMBER` across files (Q4 cumulative files can overlap; keep the latest file's row).
4. Save `data/raw/lca/lca_all.parquet`. Print rows per FY, received-date range, and the share of rows with `VISA_CLASS == "H-1B"`.

## Done when
- `lca_all.parquet` exists with the columns above (or documented equivalents)
- Test with a 20-row synthetic xlsx fixture in the real column format
- Commit `step 03: fetch LCA data`

## Notes from build
