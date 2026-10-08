-- One row per certified H-1B LCA, with an annualised wage and a role group.
with certified as (

    select
        *,
        left(soc_code, 7) as soc7
    from {{ ref('stg_lca') }}
    where visa_class = 'H-1B'
        and case_status = 'Certified'

),

-- the best (lowest priority number) title keyword for each case, if any
keyword_hits as (

    select
        certified.case_number,
        arg_min(keywords.role_group, keywords.priority) as role_group
    from certified
    inner join {{ ref('title_keywords') }} as keywords
        on contains(lower(certified.job_title), keywords.keyword)
        and (keywords.only_soc is null or keywords.only_soc = certified.soc7)
    group by certified.case_number

),

waged as (

    select
        certified.*,
        certified.wage_rate_of_pay_from * case certified.wage_unit_of_pay
            when 'Year' then 1
            when 'Month' then 12
            when 'Bi-Weekly' then 26
            when 'Week' then 52
            when 'Hour' then 2080
        end as raw_annual_wage
    from certified

)

select
    waged.case_number,
    coalesce(waged.received_date, waged.decision_date) as event_date,
    waged.received_date,
    waged.decision_date,
    waged.employer_name,
    waged.trade_name_dba,
    waged.employer_address1,
    waged.employer_city,
    waged.employer_state,
    waged.employer_zip5,
    waged.worksite_city,
    waged.worksite_state,
    waged.worksite_zip5,
    waged.job_title,
    waged.soc7 as soc_code,
    waged.soc_title,
    waged.total_worker_positions,
    (waged.new_employment > 0 or waged.change_employer > 0) as is_new_hire,
    -- wages outside $20k to $1M a year are data-entry errors, not pay
    case
        when waged.raw_annual_wage between 20000 and 1000000 then round(waged.raw_annual_wage)
    end as annual_wage,
    coalesce(
        keyword_hits.role_group,
        soc_groups.role_group,
        case when waged.soc7 like '15-%' then 'Other tech' else 'Non-tech' end
    ) as role_group,
    case when waged.pw_wage_level in ('I', 'II', 'III', 'IV') then waged.pw_wage_level end
        as pw_wage_level
from waged
left join keyword_hits
    on waged.case_number = keyword_hits.case_number
left join {{ ref('soc_role_groups') }} as soc_groups
    on waged.soc7 = soc_groups.soc_code
