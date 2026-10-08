select
    trim("CASE_NUMBER") as case_number,
    trim("CASE_STATUS") as case_status,
    cast("RECEIVED_DATE" as date) as received_date,
    cast("DECISION_DATE" as date) as decision_date,
    trim("VISA_CLASS") as visa_class,
    nullif(regexp_replace(trim("JOB_TITLE"), '\s+', ' ', 'g'), '') as job_title,
    nullif(trim("SOC_CODE"), '') as soc_code,
    nullif(trim("SOC_TITLE"), '') as soc_title,
    upper(trim("FULL_TIME_POSITION")) = 'Y' as is_full_time,
    cast("BEGIN_DATE" as date) as begin_date,
    cast("TOTAL_WORKER_POSITIONS" as integer) as total_worker_positions,
    coalesce(cast("NEW_EMPLOYMENT" as integer), 0) as new_employment,
    coalesce(cast("CONTINUED_EMPLOYMENT" as integer), 0) as continued_employment,
    coalesce(cast("CHANGE_EMPLOYER" as integer), 0) as change_employer,
    nullif(regexp_replace(trim("EMPLOYER_NAME"), '\s+', ' ', 'g'), '') as employer_name,
    nullif(regexp_replace(trim("TRADE_NAME_DBA"), '\s+', ' ', 'g'), '') as trade_name_dba,
    nullif(trim("EMPLOYER_ADDRESS1"), '') as employer_address1,
    nullif(trim("EMPLOYER_CITY"), '') as employer_city,
    nullif(upper(trim("EMPLOYER_STATE")), '') as employer_state,
    nullif(trim("EMPLOYER_POSTAL_CODE"), '') as employer_postal_code,
    case
        when regexp_matches(trim("EMPLOYER_POSTAL_CODE"), '^[0-9]{5}')
            then left(trim("EMPLOYER_POSTAL_CODE"), 5)
    end as employer_zip5,
    nullif(trim("NAICS_CODE"), '') as naics_code,
    nullif(trim("WORKSITE_CITY"), '') as worksite_city,
    nullif(upper(trim("WORKSITE_STATE")), '') as worksite_state,
    case
        when regexp_matches(trim("WORKSITE_POSTAL_CODE"), '^[0-9]{5}')
            then left(trim("WORKSITE_POSTAL_CODE"), 5)
    end as worksite_zip5,
    cast("WAGE_RATE_OF_PAY_FROM" as double) as wage_rate_of_pay_from,
    cast("WAGE_RATE_OF_PAY_TO" as double) as wage_rate_of_pay_to,
    nullif(trim("WAGE_UNIT_OF_PAY"), '') as wage_unit_of_pay,
    cast("PREVAILING_WAGE" as double) as prevailing_wage,
    nullif(trim("PW_UNIT_OF_PAY"), '') as pw_unit_of_pay,
    nullif(trim("PW_WAGE_LEVEL"), '') as pw_wage_level,
    fiscal_year,
    fiscal_quarter
from {{ source('lca', 'lca_all') }}
