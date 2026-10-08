-- One row per startup (SEC CIK) that has at least one Bay Area raise.
with raises as (

    select * from {{ ref('int_bay_area_raises') }}

),

latest as (

    select cik, company, city, zip5, county_name, industry
    from raises
    qualify row_number() over (
        partition by cik
        order by filing_date desc, accession desc
    ) = 1

),

totals as (

    select
        cik,
        min(filing_date) as first_raise_date,
        max(filing_date) as latest_raise_date,
        count(*) as raise_count,
        sum(amount_sold) as total_sold
    from raises
    group by cik

),

slugged as (

    select
        latest.*,
        trim(regexp_replace(lower(strip_accents(latest.company)), '[^a-z0-9]+', '-', 'g'), '-')
            as base_slug
    from latest

)

select
    slugged.cik,
    slugged.company,
    slugged.city,
    slugged.zip5,
    slugged.county_name,
    slugged.industry,
    totals.first_raise_date,
    totals.latest_raise_date,
    totals.raise_count,
    totals.total_sold,
    -- two companies with the same name get the CIK appended so every slug is unique
    case
        when slugged.base_slug = '' then 'cik-' || ltrim(slugged.cik, '0')
        when count(*) over (partition by slugged.base_slug) > 1
            then slugged.base_slug || '-' || ltrim(slugged.cik, '0')
        else slugged.base_slug
    end as company_slug
from slugged
inner join totals
    on slugged.cik = totals.cik
