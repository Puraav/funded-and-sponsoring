{{ config(materialized='view') }}

select
    trim(accession_number) as accession_number,
    cast(filing_date as date) as filing_date,
    trim(submission_type) as submission_type,
    lpad(trim(cik), 10, '0') as cik,
    nullif(regexp_replace(trim(entity_name), '\s+', ' ', 'g'), '') as entity_name,
    nullif(trim(street1), '') as street1,
    nullif(trim(city), '') as city,
    nullif(upper(trim(state)), '') as state,
    case when regexp_matches(trim(zipcode), '^[0-9]{5}') then left(trim(zipcode), 5) end as zip5,
    nullif(trim(entity_type), '') as entity_type,
    nullif(trim(industry_group), '') as industry_group,
    coalesce(is_business_combination, false) as is_business_combination,
    cast(first_sale_date as date) as first_sale_date,
    cast(amount_offered as decimal(18, 2)) as amount_offered,
    cast(amount_sold as decimal(18, 2)) as amount_sold,
    nullif(trim(officers), '') as officers
from {{ source('formd_recent', 'formd_recent') }}
