# Spec 09 — Web app (Next.js, static, Vercel)

## Data export
`python -m fundsponsor.export_site` reads the marts and writes to `web/public/data/`:
- `findings.json`, `metrics.json` (all mart_* tables), `match_quality.json`
- `companies.json` — compact index for search/filter: slug, name, city, county, industry, latest raise date, total sold, round bin, prior_24m, after_12m, role groups, median wage
- `company/<slug>.json` — one file per company **with at least one raise and at least one matched LCA**, plus every company in the radar: raises, monthly LCA counts, role/wage table, Form D executive officers (name + relationship only)
- `radar.json` (spec 10)
Keep the total under ~20 MB; print file count and size.

## Pages (App Router, TypeScript, Tailwind, Observable Plot)
1. `/` — the question in one line, 4 headline numbers, charts for sponsor rate by round and prior history, link to the radar.
2. `/explore` — client-side filters (round bin, industry, county, raise date range, sponsored before yes/no), sortable table, CSV download. Fast at a few thousand rows.
3. `/company/[slug]` — `generateStaticParams` from `companies.json`. Raise timeline, monthly LCA bars, roles and wages table, executive officers, links to the SEC filing.
4. `/radar` — this week's ranked list with the reasons for each score and the date it was generated.
5. `/method` — sources with links, definitions, match quality numbers, limitations:
   - an LCA is an application step, not an approved H-1B or an actual hire
   - Form D is filed by many but not all startups; some file late or not at all
   - matching relies on legal names; renamed companies or HQ moves can be missed
   - Form D amounts are self-reported

## Quality bar
- Mobile-first; works at 375 px wide; light and dark mode
- Each page has a title + Open Graph meta (so LinkedIn previews look right); a static OG image for `/`
- Lighthouse ≥ 90 for performance and accessibility on `/` (print the scores)
- Playwright smoke test: `/`, `/explore` (apply a filter), one company page, `/radar` load without console errors

## Done when
- `npm run lint` and `npm run build` pass; `out/` is generated
- Smoke test passes; Lighthouse scores printed
- Commit `step 09: web app`
