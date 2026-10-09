# Spec 08 — PNG charts (for README and LinkedIn)

The site draws interactive charts (spec 09); these are static images for the README and LinkedIn. `python -m fundsponsor.charts` reads the marts from DuckDB with matplotlib.

Style: 1600×1000 px, 200 dpi, white background. Title = the finding with its number (not "Sponsor rate by round"). Subtitle = definition + n. Source line: "Source: SEC Form D, DOL LCA disclosure data · github.com/Puraav/funded-and-sponsoring". One accent colour on the point being made; everything else grey.

1. `01_sponsor_rate_by_round.png` — horizontal bars by round bin, n on each bar
2. `02_prior_history.png` — sponsored before raising vs not → sponsor rate after
3. `03_roles_and_wages.png` — post-raise LCAs by role group, median wage labelled
4. `04_entry_level.png` — share of sponsoring startups with an entry-level tech LCA
5. `05_days_to_first_lca.png` — histogram, median marked
6. `06_match_quality.png` — startups, matched, precision per tier

## Done when
- All PNGs in `charts/`; open each and check nothing overlaps or is cut off
- Commit `step 08: charts`

## Notes from build
- Every title is built from the mart numbers at draw time, so it cannot drift from the data.
- Chart 5 is a real histogram in equal 30-day steps, drawn from `fct_raises.days_to_first_lca`. The `mart_time_to_lca` buckets are uneven (30 and 90 days wide) and would mislead as bars; the mart still supplies the median, quartile and n.
- Chart 4 is one bar split in two (45% / 55%) rather than a pie.
- Chart 6 shows matched pairs per rule with the checked-sample result written on each bar.
- Accent colour `#2a78d6`, everything else grey; text is always dark ink, never the accent.
- Each PNG was opened and checked: no overlapping or cut-off labels.
