-- How much of Bay Area H-1B sponsorship comes from the startups in this project:
-- by distinct employer (normalised name) and by number of filings.
with bay_area as (

    select
        lca.case_number,
        {{ normalise_name('lca.employer_name') }} as employer_key,
        matches.cik is not null as is_startup
    from {{ ref('int_lca_h1b') }} as lca
    inner join {{ ref('bay_area_zips') }} as zips
        on lca.employer_zip5 = zips.zip
    left join {{ ref('int_matches') }} as matches
        on lca.employer_name = matches.employer_name
        and lca.employer_zip5 = matches.employer_zip5

),

employers as (

    select employer_key, bool_or(is_startup) as is_startup
    from bay_area
    where employer_key is not null
    group by employer_key

)

select
    (select count(*) from employers) as n,
    (select count(*) from employers where is_startup) as startup_employers,
    (select count(*) from employers where is_startup) / (select count(*) from employers)
        as employer_share,
    (select count(*) from bay_area) as lcas,
    (select count(*) from bay_area where is_startup) as startup_lcas,
    (select count(*) from bay_area where is_startup) / (select count(*) from bay_area)
        as lca_share,
    (select count(*) from employers) < 30 as small_sample
