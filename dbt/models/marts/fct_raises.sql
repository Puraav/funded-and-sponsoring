-- One row per startup raise, with the H-1B filings of the same company before and after it.
with raises as (

    select * from {{ ref('int_bay_area_raises') }}

),

events as (

    select * from {{ ref('fct_lca_events') }}

),

-- the last day the LCA data covers; a raise needs a full year after it to be judged
coverage as (

    select max(event_date) as last_event_date from {{ ref('int_lca_h1b') }}

),

windows as (

    select
        raises.accession,
        events.case_number,
        events.event_date,
        events.is_new_hire,
        events.role_group,
        events.annual_wage,
        (
            events.event_date >= raises.filing_date - interval 24 month
            and events.event_date < raises.filing_date
        ) as is_prior,
        (
            events.event_date >= raises.filing_date
            and events.event_date <= raises.filing_date + interval 12 month
        ) as is_after
    from raises
    inner join events
        on raises.cik = events.cik

),

counted as (

    select
        accession,
        count(*) filter (where is_prior) as prior_24m,
        count(*) filter (where is_after) as after_12m,
        count(*) filter (where is_after and is_new_hire) as after_12m_new_hire,
        count(*) filter (where is_after and role_group = 'Software') as after_software,
        count(*) filter (where is_after and role_group = 'Data') as after_data,
        count(*) filter (where is_after and role_group = 'Product') as after_product,
        count(*) filter (where is_after and role_group = 'Other tech') as after_other_tech,
        count(*) filter (where is_after and role_group = 'Non-tech') as after_non_tech,
        median(annual_wage) filter (where is_after) as median_wage_after,
        min(event_date) filter (where is_after) as first_lca_after
    from windows
    group by accession

)

select
    raises.accession,
    raises.cik,
    raises.company,
    raises.city,
    raises.county_name,
    raises.industry,
    raises.filing_date,
    raises.first_sale_date,
    raises.amount_sold,
    raises.amount_offered,
    raises.round_bin,
    raises.is_first_raise,
    coalesce(counted.prior_24m, 0) as prior_24m,
    coalesce(counted.after_12m, 0) as after_12m,
    coalesce(counted.after_12m_new_hire, 0) as after_12m_new_hire,
    coalesce(counted.after_12m, 0) > 0 as sponsored_after,
    coalesce(counted.after_12m_new_hire, 0) > 0 as sponsored_after_new_hire,
    coalesce(counted.after_software, 0) as after_software,
    coalesce(counted.after_data, 0) as after_data,
    coalesce(counted.after_product, 0) as after_product,
    coalesce(counted.after_other_tech, 0) as after_other_tech,
    coalesce(counted.after_non_tech, 0) as after_non_tech,
    counted.median_wage_after,
    counted.first_lca_after,
    date_diff('day', raises.filing_date, counted.first_lca_after) as days_to_first_lca,
    raises.filing_date <= coverage.last_event_date - interval 365 day as has_full_followup
from raises
cross join coverage
left join counted
    on raises.accession = counted.accession
