# Spec 10 — The radar (recent raises, weekly)

The quarterly Form D data sets lag up to 3 months. The radar reads **new filings straight from EDGAR**.

## Ingest: `python -m fundsponsor.fetch_edgar_recent --days 30`
- EDGAR daily form index: `https://www.sec.gov/Archives/edgar/daily-index/{YYYY}/QTR{Q}/form.{YYYYMMDD}.idx` → rows with form type `D`
- Each filing: `https://www.sec.gov/Archives/edgar/data/{CIK}/{ACCESSION_NO_DASHES}/primary_doc.xml` → issuer name, address, ZIP, industry group, total amount sold, date of first sale, related persons
- Declared User-Agent, ≤5 requests/second, cache each XML under `data/raw/edgar/`
- Output `data/raw/formd_recent.parquet` in the same shape as the staging models expect

## dbt
- `stg_formd_recent` → reuse the spec 04 logic (factor the shared filters into a macro) → `int_recent_raises`
- Match with the spec 06 macros against `int_lca_h1b` (tiers 1–3 only)
- `radar` model, score 0–100, documented in the model `.yml` and on `/method`:
  - 40 pts — H-1B LCAs in the last 24 months (log-scaled, capped)
  - 25 pts — any Software/Data/Product LCAs
  - 15 pts — any Level I/II LCAs (hires early-career)
  - 20 pts — amount raised (by round bin)
  - a `reasons` column in plain words: "12 H-1B filings since 2024, 5 for software roles, 2 entry-level"
- Test: score between 0 and 100; one row per accession

## Output
`export_site` writes `radar.json`; also write `radar/radar_YYYY-MM-DD.md` (top 25: company, city, raised, score, reasons, SEC link).

## Weekly GitHub Action `radar.yml`
Monday 14:00 UTC: fetch recent → `dbt build --select +radar` → export → commit `radar/` and `web/public/data/radar.json` → Vercel redeploys from the push. Uses repo secret `SEC_USER_AGENT`. The LCA parquet is too big for Actions: export a small `lca_employer_history.parquet` (employer key, counts by role/level, last 24 months) to `data/seed_cache/`, commit it, and let the action use that.

## Out of scope (on purpose)
No automatic emails or LinkedIn messages to companies. Outreach stays personal.

## Done when
- The command prints the top 10 with reasons
- Tests with two saved `primary_doc.xml` fixtures
- Commit `step 10: radar`

## Notes from build
- **The radar reads two small committed extracts, not the warehouse.** `data/seed_cache/lca_employer_history.parquet` (certified H-1B LCAs per California employer per month, with role and early-career counts; 88,411 rows, 0.6 MB) and `listed_ciks.parquet` (1,816 CIKs of listed companies). They are dbt marts (`mart_lca_employer_history`, `mart_listed_ciks`) copied out by `python -m fundsponsor.export_seed_cache`. The radar models read them as dbt sources, so the same SQL runs locally and in the Action. Re-run the export after refreshing the LCA or Form D data.
- **`formd_recent.parquet` is one flat row per filing**, not four tables: accession, date, type, issuer name and address, entity type, industry, business-combination flag, first sale date, amounts, and the executive officers' names. Addresses of related persons are never read.
- **Shared filters:** the fund / SPV / merger / LLC rules moved into the `startup_filters` macro, used by both `int_bay_area_raises` and `int_recent_raises`. Recent filings have no SIC code, so listed companies are removed with the `listed_ciks` extract instead.
- **Matching** is `int_recent_matches`: rules 1 to 3 on the normalised name, the generic-name rule, and the same drop-on-tie rule. No fuzzy rule, as specified.
- **"Last 24 months" is the 24 months before the raise.** LCA data currently ends in June 2026, so for an October 2026 raise the last three months are not yet visible.
- **Score:** 40 x min(1, ln(1 + filings) / ln(51)), so 50 filings earns the full 40; plus 25, 15 and the round-size points. Documented in `_radar.yml`, the README and `/method`.
- **Model tag and selection:** the radar models live in `dbt/models/radar/` with the tag `radar`. The Action runs `dbt build --select +radar --indirect-selection=cautious`; without `cautious`, dbt also tries a test that needs `int_bay_area_raises`, which the Action does not build.
- **Exporter is separate:** `python -m fundsponsor.export_radar` writes `web/public/data/radar.json` (top 50) and `radar/radar_YYYY-MM-DD.md` (top 25). It reads only the `radar` tables, so it works in the Action. Links to company pages come from the committed `companies.json`.
- **Not done: a page for every radar company.** The spec asks for a company page for each radar entry. Only startups that already have a page (a raise in the quarterly data and a matched filing) are linked; a startup whose first Form D is in the last few weeks is listed with its reasons and SEC link but has no page until the next quarterly refresh.
- **EDGAR details:** a day with no index (weekend, holiday) answers 403, not 404. A filing with co-issuers is listed once per issuer, so index rows are de-duplicated by accession. One HTTP connection is reused, which took the fetch from about 1.5 to about 4 requests a second.
- **Real run on 2026-10-09:** 3,854 Form D filings listed for 2026-09-09 to 2026-10-08 (1 unreadable), 460 in California, 76 Bay Area startups after the filters. Top of the radar: Harvey AI (99), Superhuman Platform (96), Twin Health (90), Incode Technologies (83), Voxel Labs (80).
- **Action checked locally:** the exact Action steps were run against an empty warehouse and produced a byte-identical `radar.json`. The fetch takes about 15 to 25 minutes without a cache; the workflow caches `data/raw/edgar` between runs.
- **Fixtures:** three synthetic `primary_doc.xml` files in `tests/fixtures/edgar/` (a startup with history, a fund, a startup with none). The expected score of 77 for the first is worked out by hand in `tests/test_radar.py`.
