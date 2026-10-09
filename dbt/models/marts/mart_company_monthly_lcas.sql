-- H-1B filings per startup per month, for the bar chart on each company page.
select
    cik,
    cast(date_trunc('month', event_date) as date) as month,
    count(*) as lcas,
    count(*) filter (where is_new_hire) as new_hire_lcas
from {{ ref('fct_lca_events') }}
group by cik, cast(date_trunc('month', event_date) as date)
