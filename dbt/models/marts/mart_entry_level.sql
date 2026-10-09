-- Of the startups that file after raising, how many file for an early-career tech role:
-- a Software, Data or Product LCA at prevailing wage Level I or II.
with sponsors as (

    select distinct cik
    from {{ ref('fct_raises') }}
    where has_full_followup and sponsored_after

),

entry_level as (

    select distinct cik
    from {{ ref('int_post_raise_lcas') }}
    where role_group in ('Software', 'Data', 'Product')
        and pw_wage_level in ('I', 'II')

)

select
    count(*) as n,
    count(entry_level.cik) as with_entry_level,
    count(entry_level.cik) / count(*) as entry_level_share,
    count(*) < 30 as small_sample
from sponsors
left join entry_level
    on sponsors.cik = entry_level.cik
