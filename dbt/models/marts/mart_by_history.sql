-- Does sponsoring before a raise predict sponsoring after it?
select
    case when prior_24m >= 1 then 'sponsored_before' else 'no_prior' end as history,
    case
        when prior_24m >= 1 then 'Filed for H-1B workers in the 24 months before'
        else 'No H-1B filing in the 24 months before'
    end as history_label,
    count(*) as n,
    count(*) filter (where sponsored_after) as sponsored,
    count(*) filter (where sponsored_after) / count(*) as sponsor_rate,
    count(*) < 30 as small_sample
from {{ ref('fct_raises') }}
where has_full_followup
group by 1, 2
