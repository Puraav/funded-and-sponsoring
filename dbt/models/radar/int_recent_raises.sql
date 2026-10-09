-- Recent Form D filings that pass the same startup rules as the quarterly raises.
with recent as (

    select
        accession_number as accession,
        cik,
        entity_name as company,
        street1 as street,
        city,
        zip5,
        industry_group as industry,
        entity_type,
        is_business_combination,
        filing_date,
        first_sale_date,
        amount_sold,
        amount_offered,
        officers
    from {{ ref('stg_formd_recent') }}
    where submission_type = 'D'

)

select
    recent.accession,
    recent.cik,
    recent.company,
    recent.street,
    recent.city,
    recent.zip5,
    zips.county_name,
    recent.industry,
    recent.filing_date,
    recent.first_sale_date,
    recent.amount_sold,
    recent.amount_offered,
    case
        when recent.amount_sold is null or recent.amount_sold <= 0 then 'unknown'
        when recent.amount_sold < 2000000 then '<$2M'
        when recent.amount_sold < 10000000 then '$2–10M'
        when recent.amount_sold < 50000000 then '$10–50M'
        else '$50M+'
    end as round_bin,
    recent.officers
from recent
inner join {{ ref('bay_area_zips') }} as zips
    on recent.zip5 = zips.zip
where {{ startup_filters('recent') }}
    and recent.cik not in (select cik from {{ source('seed_cache', 'listed_ciks') }})
