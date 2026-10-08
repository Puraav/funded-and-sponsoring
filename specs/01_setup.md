# Spec 01 — Project setup (Python + dbt + web skeleton + CI)

## Build
1. **Python:** `pyproject.toml` with package `fundsponsor` in `ingest/` (Python ≥3.11), deps from CLAUDE.md, `dev` extra with pytest + ruff (line length 100). Stub modules for every file in the layout, each with a docstring and `main()` printing "not built yet".
2. **Config:** `ingest/config.py` with `ROOT`, `RAW_DIR`, `CHARTS_DIR`, `WAREHOUSE = data/warehouse.duckdb`, `WEB_DATA_DIR = web/public/data`; `FS_DATA_DIR` env override for tests; `SEC_USER_AGENT` from `.env` with a clear error if missing when an SEC call is made; `BAY_AREA_COUNTIES`.
3. **dbt:** `dbt/` project named `fundsponsor`, profile in `dbt/profiles.yml` (committed, no secrets) using dbt-duckdb with `path: ../data/warehouse.duckdb`. `packages.yml` with `dbt_utils`. A `vars` block `raw_dir` defaulting to `../data/raw` (overridable by env `FS_DATA_DIR`). Empty `models/staging|intermediate|marts`, `seeds/`, `tests/`.
4. **Web:** `web/` via `create-next-app` (TypeScript, Tailwind, App Router, ESLint, no `src/`), `next.config` with `output: 'export'` and `images.unoptimized: true`. Install `@observablehq/plot`. One placeholder page that says "Funded & Sponsoring — coming soon".
5. `.env.example`, `.gitignore` (`.venv/`, `.env`, `data/raw/`, `data/*.duckdb`, `dbt/target/`, `dbt/dbt_packages/`, `dbt/logs/`, `web/node_modules/`, `web/.next/`, `web/out/`, `__pycache__/`, `*.part`).
6. **CI** `.github/workflows/ci.yml`, three jobs:
   - python: install, `ruff check .`, `pytest -q`
   - dbt: install, `dbt deps`, `dbt seed`, `dbt build` with `FS_DATA_DIR=tests/fixtures/raw` (fixtures come in later specs; until then `dbt debug` only)
   - web: Node 20, `npm ci`, `npm run lint`, `npm run build`
7. `tests/test_smoke.py` imports every module. Placeholder `README.md`.

## Done when
- `pip install -e ".[dev]"`, `dbt debug`, `npm run build` all succeed locally
- `ruff check .` clean, `pytest -q` green
- Commit `step 01: project setup`
