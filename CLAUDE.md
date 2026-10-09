# CLAUDE.md — project rules for Claude Code

## What this project is
**Funded & Sponsoring** — a public portfolio project. It answers:

> Of the Bay Area startups that raise money, how many file for H-1B workers within a year, for which roles, and at what pay? And which startups raised money recently and have a history of sponsoring?

It joins two free public datasets that nobody joins today:
- **SEC Form D filings** (who raised money, when, how much, where)
- **DOL LCA disclosure data** (which employers filed H-1B wage applications, for which job, at what wage)

It deliberately shows three skills:
1. **Python** for ingestion (downloading and parsing public files)
2. **SQL + dbt on DuckDB** for all transformation, matching, metrics and tests
3. **A Next.js + TypeScript web app** (static, deployed on Vercel) as the product people use

Everything is built from public data and must be reproducible by anyone.

## How to work
- Work **only** on the spec the user points to (`specs/0X_*.md`). Don't build ahead.
- After implementing, run that spec's **"Done when"** checks and show the output.
- Commit at the end of each spec: `step 03: fetch LCA data`.
- If a spec is ambiguous, pick the simplest option and say so in one line.
- **Never invent data or hardcode results.** Every number in the README, charts and site comes from the dbt models.
- If a real file doesn't match the columns a spec expects, print the actual columns, adapt, and note it under "Notes from build" in that spec.
- No secrets in code or commits. The SEC User-Agent contact goes in `.env` (`SEC_USER_AGENT="Puraav Ghuwalewala puraav11@gmail.com"`).
- **Transformations belong in dbt SQL, not pandas.** Python only downloads, parses raw files to parquet, exports JSON for the site, and draws PNG charts.

## Tech stack (don't swap without asking)
- **Ingest:** Python 3.11+, `.venv`, `pyproject.toml` with a `dev` extra: requests, python-dotenv, pyarrow, pandas (parsing only), openpyxl, lxml, duckdb, matplotlib
- **Transform:** dbt-core + dbt-duckdb, `dbt_utils` package; DuckDB file at `data/warehouse.duckdb`
- **Web:** Next.js (App Router) + TypeScript + Tailwind, `output: 'export'` (fully static), Observable Plot for charts, deployed on Vercel
- **Quality:** pytest + ruff (Python), dbt tests, ESLint + `next build` (web), Playwright smoke test
- **CI:** GitHub Actions: ruff, pytest, `dbt build` on fixtures, web lint + build

## Layout
```
ingest/                      Python package `fundsponsor`
  config.py                  paths, URLs, constants
  fetch_formd.py             SEC Form D quarterly data sets → data/raw/formd/*.parquet
  fetch_lca.py               DOL LCA files → data/raw/lca/lca_all.parquet
  fetch_edgar_recent.py      last N days of Form D XML from EDGAR (radar)
  make_seeds.py              Census ZCTA→county → dbt seed
  match_sample.py            matches → data/match_sample.csv for hand-labelling
  export_site.py             dbt marts → web/public/data/*.json
  findings.py                marts → findings.json + README block
  charts.py                  marts → charts/*.png (README + LinkedIn)
dbt/                         dbt project `fundsponsor`
  models/staging/            stg_formd_*, stg_lca
  models/intermediate/       int_bay_area_raises, int_lca_h1b, int_name_keys, int_matches
  models/marts/              dim_company, fct_raises, fct_lca_events, mart_* metrics, radar
  seeds/                     bay_area_zips, soc_role_groups, fund_name_patterns, match_labels
  tests/                     singular tests
web/                         Next.js app
tests/                       pytest + fixtures (tiny SYNTHETIC files in real formats)
data/raw/ (gitignored)  data/warehouse.duckdb (gitignored)  charts/
```

## Conventions
- Paths and constants in `ingest/config.py`; dbt reads raw parquet paths from `vars` / env var `FS_DATA_DIR`, so CI can point it at fixtures.
- dbt naming: `stg_` = 1:1 with a source, cleaned; `int_` = joins/logic; `fct_`/`dim_` = final tables; `mart_` = aggregated metrics. Every model has a `.yml` entry with a description and column tests.
- ZIP codes are 5-character strings. Money in US dollars; wages annualised.
- Scripts print short summaries (row counts, totals) so results can be checked.
- Be polite to SEC: declared User-Agent, max 5 requests/second, retries with backoff, cache on disk.

## Definitions (use these everywhere)
- **Bay Area** = 9 counties: Alameda 06001, Contra Costa 06013, Marin 06041, Napa 06055, San Francisco 06075, San Mateo 06081, Santa Clara 06085, Solano 06095, Sonoma 06097. ZIP → county from the Census 2020 ZCTA–county relationship file (largest land-area overlap wins).
- **Startup raise** = an original Form D (`SUBMISSIONTYPE` = `D`, not `D/A`) from a Bay Area issuer that is an operating company, not a fund (spec 04).
- **Sponsoring event** = a **certified H-1B** LCA (`VISA_CLASS` = `H-1B`, `CASE_STATUS` = `Certified`) whose employer matches the startup.
- **New-hire LCA** = `NEW_EMPLOYMENT` > 0 or `CHANGE_EMPLOYER` > 0.
- An LCA is a step **before** an H-1B petition. Always say "filed for H-1B workers", never "hired H-1B workers".

## Commands (keep these working)
- `python -m fundsponsor.fetch_formd` · `python -m fundsponsor.fetch_lca` · `python -m fundsponsor.make_seeds`
- `cd dbt && dbt deps && dbt seed && dbt build` · `dbt docs generate`
- `python -m fundsponsor.findings` · `python -m fundsponsor.charts` · `python -m fundsponsor.export_site`
- `python -m fundsponsor.export_seed_cache` (after a full `dbt build`) · `python -m fundsponsor.fetch_edgar_recent --days 30 && cd dbt && dbt build --select +radar --indirect-selection=cautious` · `python -m fundsponsor.export_radar`
- `cd web && npm run dev` · `npm run build` · `npx playwright test`
- `pytest -q` · `ruff check .`
