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
- **The files are not cumulative.** For FY2023 to FY2025 each `Q{n}` file holds one quarter of decisions, so the Q4 file is not the full year (FY2023 Q4 has 128k rows; the year has 525k). All four quarters of each year are downloaded: 12 files. FY2026 has a single file, `FY2026_Q3`, which is cumulative for October 2025 to June 2026.
- **FY2026 URL differs:** `https://www.dol.gov/media/LCA_Disclosure_Data_FY2026_Q3.xlsx`, not the `/sites/dolgov/files/ETA/oflc/pdfs/` pattern. `config.LCA_FILES` lists every URL explicitly.
- **dol.gov rejects browser look-alike User-Agents** (403 from Akamai) but serves an honest descriptive one, so the downloader sends `fundsponsor research (github.com/Puraav/funded-and-sponsoring)`.
- **Header matches the spec.** All 30 wanted columns exist under those exact names (the file has 96 columns). An alias map covers the older `_1`-suffixed names in case a file uses them.
- **Text cells are wrapped as Excel formulas**, e.g. `="07310"`, `="15-1252.00"`, `=""`. The wrapper is stripped; `=""` becomes null.
- **Cases repeat across quarterly files** (a case certified in one quarter and withdrawn in a later one appears in both): 2,239,692 rows read, 2,095,023 after keeping the latest file's row per `CASE_NUMBER`.
- Three columns are added: `fiscal_year`, `fiscal_quarter`, `source_file`.
- Real run on 2026-10-08: FY2023 524,894 rows, FY2024 546,490, FY2025 586,143, FY2026 (to June) 437,496. Decision dates 2022-10-01 to 2026-06-30; received dates 2019-10-03 to 2026-06-30. 97.5% are `H-1B`; the rest are `E-3 Australian`, `H-1B1 Chile`, `H-1B1 Singapore`. Statuses: `Certified`, `Certified - Withdrawn`, `Withdrawn`, `Denied`.
- `PW_WAGE_LEVEL` is null on about 7% of rows and `N/A` on a few more (prevailing wage from a non-OES source). `EMPLOYER_POSTAL_CODE` is ZIP+4 on about 1% of rows.
- The raw download is 1.6 GB of Excel; `lca_all.parquet` is 110 MB. Conversion takes about 80 seconds with 8 workers.
