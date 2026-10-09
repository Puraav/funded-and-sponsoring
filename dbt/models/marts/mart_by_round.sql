-- Sponsor rate by size of raise, for raises with a full year of follow-up.
select
    round_bin,
    case round_bin
        when '<$2M' then 1
        when '$2–10M' then 2
        when '$10–50M' then 3
        when '$50M+' then 4
        else 5
    end as round_order,
    count(*) as n,
    count(*) filter (where sponsored_after) as sponsored,
    count(*) filter (where sponsored_after) / count(*) as sponsor_rate,
    median(after_12m) filter (where sponsored_after) as median_lcas_per_sponsor,
    count(*) < 30 as small_sample
from {{ ref('fct_raises') }}
where has_full_followup
group by round_bin
