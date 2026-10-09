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

## Notes from build
- **Next.js 16.** `create-next-app` installed Next 16.4 with Tailwind 4. `cacheComponents` and `partialPrefetching` from its template were removed, as they do not apply to a static export.
- **Four small dbt marts were added for the site**, so Python only dumps tables: `mart_companies` (the Explore index), `mart_company_monthly_lcas`, `mart_company_roles`, `mart_company_officers`.
- **Pages:** 504 company pages (startups with at least one matched H-1B filing), plus `/`, `/explore`, `/radar`, `/method`. Explore lists all 1,614 startups; those without a matched filing are shown without a link.
- **Data size:** 509 JSON files, 1.2 MB, committed under `web/public/data/` so Vercel can build without the pipeline.
- **Charts** are Observable Plot, loaded on demand after first paint, each with a "View as table" fallback and hover tooltips. The site's charts use the same accent-on-grey style as the PNGs.
- **Explore** renders 100 rows at a time with a "Show more" button; filters and sorting run over all rows in memory. CSV download exports the filtered rows.
- **Dark mode** follows the system setting. Checked at 375 px wide in dark mode: no sideways scrolling on any page (also asserted in the smoke test).
- **Open Graph:** each page has its own title and description; the preview image `web/public/og.png` (1200 x 630) is drawn by `python -m fundsponsor.charts` from the headline mart. `lib/site.ts` holds the site URL, defaulting to `https://funded-and-sponsoring.vercel.app` until the real one is known (`NEXT_PUBLIC_SITE_URL` overrides it).
- **Officers:** name and relationship only. Addresses on the Form D are never exported (asserted in `tests/test_export_site.py`).
- **Smoke test:** `npx playwright test` runs 5 tests against the static export served by `scripts/serve-out.mjs` (clean URLs and gzip, like the real host). All pass with no console errors.
- **Lighthouse on `/` (mobile, simulated throttling):** performance 98, accessibility 100. The first run scored 75 / 95: the local server sent files uncompressed, and Plot's internal `aria-label`s on `<g>` elements are invalid ARIA. Both fixed (gzip in the test server; inner labels removed, the wrapper carries the chart's label).
- The radar page shows an empty state until spec 10 fills `radar.json`.
