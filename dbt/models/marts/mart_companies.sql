-- One row per startup for the website's search and filter table.
with latest_raise as (

    select *
    from {{ ref('fct_raises') }}
    qualify row_number() over (partition by cik order by filing_date desc, accession desc) = 1

),

lcas as (

    select
        cik,
        count(*) as lcas_total,
        median(annual_wage) as median_wage,
        min(event_date) as first_lca_date,
        max(event_date) as latest_lca_date,
        string_agg(distinct role_group, ', ' order by role_group) as role_groups
    from {{ ref('fct_lca_events') }}
    group by cik

)

select
    companies.company_slug,
    companies.cik,
    companies.company,
    companies.city,
    companies.county_name,
    companies.industry,
    companies.first_raise_date,
    companies.latest_raise_date,
    companies.raise_count,
    companies.total_sold,
    latest_raise.round_bin,
    latest_raise.amount_sold as latest_amount_sold,
    latest_raise.prior_24m,
    latest_raise.after_12m,
    latest_raise.prior_24m > 0 as sponsored_before,
    latest_raise.has_full_followup,
    coalesce(lcas.lcas_total, 0) as lcas_total,
    lcas.median_wage,
    lcas.first_lca_date,
    lcas.latest_lca_date,
    lcas.role_groups,
    coalesce(lcas.lcas_total, 0) > 0 as has_page
from {{ ref('dim_company') }} as companies
inner join latest_raise
    on companies.cik = latest_raise.cik
left join lcas
    on companies.cik = lcas.cik
