-- Sponsor rate for the eight industries with the most raises (full follow-up only).
select
    industry,
    count(*) as n,
    count(*) filter (where sponsored_after) as sponsored,
    count(*) filter (where sponsored_after) / count(*) as sponsor_rate,
    count(*) < 30 as small_sample
from {{ ref('fct_raises') }}
where has_full_followup
group by industry
order by n desc, industry
limit 8
