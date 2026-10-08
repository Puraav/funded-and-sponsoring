# Spec 11 — README, final checks, publish, deploy

## README
1. Title, one-line question, CI badge, **link to the live site**
2. **Headline findings** (FINDINGS block from spec 07)
3. Charts 01–03
4. **Why this is new:** funding trackers (built for sales teams) and visa sponsor databases (backward-looking, mostly big companies) exist separately; this joins them to ask whether raising money leads to sponsoring, and to spot recently funded sponsors early
5. **How it's built:** a short diagram (Python ingest → DuckDB + dbt → JSON → Next.js on Vercel), `docs/lineage.png`, and the count of dbt models and tests
6. **The radar** — what it is, how the score works, link to the latest `radar/*.md`
7. Data sources with links; definitions; **match quality** numbers
8. Limitations (from spec 09)
9. Run it yourself; project structure
10. **Why I built this** — leave `<!-- PURAAV: 2–3 sentences in your words -->`
11. License MIT

## Final checks
- `ruff check .`, `pytest -q`, `dbt build`, `npm run lint`, `npm run build`, Playwright all green; CI green on GitHub
- A test asserts every number in the README matches `findings.json`
- Nothing from `data/raw/` or the DuckDB file committed; repo < 50 MB

## Publish
- `gh repo create Puraav/funded-and-sponsoring --public --source . --push`
- Description: "Which Bay Area startups that raise money go on to file for H-1B workers? SEC Form D × DOL LCA data in DuckDB + dbt, with a weekly radar of recently funded sponsors."
- Topics: h1b, international-students, startups, venture-capital, sec-edgar, dbt, duckdb, nextjs, entity-resolution, open-data

## Deploy (Vercel, user clicks)
Claude Code prepares `web/` so Vercel needs no settings beyond Root Directory = `web`. User: vercel.com → Add New Project → import the repo → Root Directory `web` → Deploy. Then put the URL in the README, the repo "Website" field and `web` OG metadata.

## Done when
- Public repo and live site both load logged out
- Commit `step 11: README, publish, deploy`
