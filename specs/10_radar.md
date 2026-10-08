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
