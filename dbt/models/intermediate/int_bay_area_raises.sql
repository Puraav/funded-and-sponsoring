-- One row per startup raise: an original Form D from a Bay Area operating company.
with originals as (

    select
        submissions.accession_number,
        issuers.cik,
        issuers.entity_name as company,
        issuers.street1 as street,
        issuers.city,
        issuers.state,
        issuers.zip5,
        offerings.industry_group as industry,
        issuers.entity_type,
        offerings.is_business_combination,
        submissions.sic_code,
        submissions.filing_date,
        offerings.first_sale_date,
        offerings.amount_sold,
        offerings.amount_offered,
        -- first original Form D we can see for this company (the data starts in Oct 2022)
        row_number() over (
            partition by issuers.cik
            order by submissions.filing_date, submissions.accession_number
        ) = 1 as is_first_raise
    from {{ ref('stg_formd_submissions') }} as submissions
    inner join {{ ref('stg_formd_issuers') }} as issuers
        on submissions.accession_number = issuers.accession_number
        and issuers.is_primary_issuer
    inner join {{ ref('stg_formd_offerings') }} as offerings
        on submissions.accession_number = offerings.accession_number
    where submissions.submission_type = 'D'

)

select
    originals.accession_number as accession,
    originals.cik,
    originals.company,
    originals.street,
    originals.city,
    originals.zip5,
    zips.county_name,
    originals.industry,
    originals.filing_date,
    originals.first_sale_date,
    originals.amount_sold,
    originals.amount_offered,
    case
        when originals.amount_sold is null or originals.amount_sold <= 0 then 'unknown'
        when originals.amount_sold < 2000000 then '<$2M'
        when originals.amount_sold < 10000000 then '$2–10M'
        when originals.amount_sold < 50000000 then '$10–50M'
        else '$50M+'
    end as round_bin,
    originals.is_first_raise
from originals
inner join {{ ref('bay_area_zips') }} as zips
    on originals.zip5 = zips.zip
where originals.filing_date >= date '2023-10-01'
    and {{ startup_filters('originals') }}
    -- a company with an SEC industry code is an SEC registrant, in practice a listed company
    -- selling shares privately (Intel, Synopsys), not a startup
    and originals.sic_code is null
