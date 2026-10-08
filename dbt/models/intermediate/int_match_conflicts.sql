-- Employers whose best rule points at more than one startup. Neither is kept: we cannot
-- tell which company the LCAs belong to.
with ranked as (

    select
        *,
        min(match_rule) over (partition by employer_name, employer_zip5) as best_rule
    from {{ ref('int_match_candidates') }}

)

select
    ranked.employer_name,
    ranked.employer_zip5,
    ranked.cik,
    companies.company,
    ranked.match_rule
from ranked
inner join {{ ref('dim_company') }} as companies
    on ranked.cik = companies.cik
where ranked.match_rule = ranked.best_rule
qualify count(*) over (partition by ranked.employer_name, ranked.employer_zip5) > 1
