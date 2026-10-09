-- H-1B filings per startup by role group, with median pay, for each company page.
select
    cik,
    role_group,
    count(*) as lcas,
    count(*) filter (where pw_wage_level in ('I', 'II')) as early_career_lcas,
    median(annual_wage) as median_wage,
    min(annual_wage) as min_wage,
    max(annual_wage) as max_wage
from {{ ref('fct_lca_events') }}
group by cik, role_group
