# Funded & Sponsoring

Of the Bay Area startups that raise money, how many file for H-1B workers within a year, for which
roles, and at what pay? And which startups raised recently and have sponsored before?

Work in progress. This joins two free public datasets, SEC Form D filings and DOL LCA disclosure
data, with Python for ingestion, dbt on DuckDB for modelling and a static Next.js site.

## Headline findings

<!-- FINDINGS:START -->
1. 24% of Bay Area startup raises were followed by at least one H-1B filing from the same company within a year (n = 1,230 raises). Counting only filings for new hires, not extensions, it is 21%.
2. Bigger raises file far more often: 60% of raises of $50M or more were followed by an H-1B filing (n = 109), against 6.1% of raises under $2M (n = 328). $2–10M: 19% (n = 423). $10–50M: 37% (n = 328).
3. Past behaviour is the strongest signal: startups that had filed for H-1B workers in the two years before raising filed again within a year 64% of the time (n = 259); those with no earlier filing did so 13% of the time (n = 971).
4. Software roles are 52% of the H-1B filings startups make in the year after raising, at a median offered wage of $179,982 (n = 1,363 of 2,602 filings).
5. 45% of the startups that filed after raising filed for at least one early-career tech role: a software, data or product job at prevailing wage Level I or II (n = 240 startups).
6. When a raise is followed by an H-1B filing, the first one comes a median of 98 days after the Form D, and a quarter come within 35 days (n = 292 raises).
7. These startups are a small slice of Bay Area sponsorship: 4.6% of the region's H-1B employers and 2.1% of its filings (n = 10,945 employers, 292,785 filings).

_Match quality: 504 of 1,614 startups (31%) were matched to an H-1B employer. In a checked sample, 60 of 60 matches were correct. An unmatched startup counts as not filing, so the rates above are a floor._

_Based on 2,064 raises by 1,614 startups filed from 2023-10-02 to 2026-09-30. Rates use raises up to 2025-06-23, the last with a full year of LCA data after them (the data runs to 2026-06-23). An LCA is an application step before an H-1B petition, not an approved visa or a hire._
<!-- FINDINGS:END -->
