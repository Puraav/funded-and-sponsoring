-- Headline: of raises with a full year of follow-up, the share followed by an H-1B filing.
with raises as (

    select * from {{ ref('fct_raises') }} where has_full_followup

)

select
    'any' as metric,
    'At least one H-1B filing within 12 months' as metric_label,
    count(*) as n,
    count(*) filter (where sponsored_after) as sponsored,
    count(*) filter (where sponsored_after) / count(*) as sponsor_rate,
    count(*) < 30 as small_sample
from raises

union all

select
    'new_hire' as metric,
    'At least one new-hire H-1B filing within 12 months' as metric_label,
    count(*) as n,
    count(*) filter (where sponsored_after_new_hire) as sponsored,
    count(*) filter (where sponsored_after_new_hire) / count(*) as sponsor_rate,
    count(*) < 30 as small_sample
from raises
