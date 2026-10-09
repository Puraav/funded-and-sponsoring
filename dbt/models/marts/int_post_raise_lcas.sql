-- Each H-1B filing made within 12 months after a raise by the same company, counted once
-- even when two raises of that company both precede it.
select distinct
    events.case_number,
    events.cik,
    events.event_date,
    events.role_group,
    events.pw_wage_level,
    events.annual_wage,
    events.is_new_hire,
    events.job_title
from {{ ref('fct_lca_events') }} as events
inner join {{ ref('int_bay_area_raises') }} as raises
    on events.cik = raises.cik
    and events.event_date >= raises.filing_date
    and events.event_date <= raises.filing_date + interval 12 month
