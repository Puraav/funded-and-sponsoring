-- One row per matched (startup, H-1B employer) pair. An employer belongs to one startup only.
with ranked as (

    select
        *,
        min(match_rule) over (partition by employer_name, employer_zip5) as best_rule
    from {{ ref('int_match_candidates') }}

),

best as (

    select *
    from ranked
    where match_rule = best_rule
    -- a tie between startups at the best rule is a conflict, recorded in int_match_conflicts
    qualify count(*) over (partition by employer_name, employer_zip5) = 1

)

select
    best.cik,
    companies.company,
    best.employer_name,
    best.employer_zip5,
    best.match_rule,
    case when best.match_rule <= 2 then 'high' else 'medium' end as tier
from best
inner join {{ ref('dim_company') }} as companies
    on best.cik = companies.cik
