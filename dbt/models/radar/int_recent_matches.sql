-- Match recent raises to California H-1B employers with rules 1 to 3 of the main matcher
-- (exact normalised name; same ZIP, then Bay Area, then California). No fuzzy rule here.
with startups as (

    select distinct
        cik,
        zip5,
        {{ normalise_name('company') }} as name_key
    from {{ ref('int_recent_raises') }}

),

startup_keys as (

    select
        *,
        (
            (name_key not like '% %' and length(name_key) <= 5)
            or name_key in (select name_key from {{ ref('generic_names') }})
        ) as is_generic
    from startups
    where name_key is not null

),

employers as (

    select distinct employer_name, trade_name_dba, employer_zip5
    from {{ source('seed_cache', 'lca_employer_history') }}

),

employer_keys as (

    select employer_name, employer_zip5, {{ normalise_name('employer_name') }} as name_key
    from employers

    union

    select employer_name, employer_zip5, {{ normalise_name('trade_name_dba') }} as name_key
    from employers
    where trade_name_dba is not null

),

candidates as (

    select
        startup_keys.cik,
        employer_keys.employer_name,
        employer_keys.employer_zip5,
        min(
            case
                when startup_keys.zip5 = employer_keys.employer_zip5 then 1
                when zips.zip is not null then 2
                else 3
            end
        ) as match_rule
    from startup_keys
    inner join employer_keys
        on startup_keys.name_key = employer_keys.name_key
    left join {{ ref('bay_area_zips') }} as zips
        on employer_keys.employer_zip5 = zips.zip
    -- generic names (Nova, Apex, ...) only count in the very same ZIP code
    where startup_keys.zip5 = employer_keys.employer_zip5 or not startup_keys.is_generic
    group by startup_keys.cik, employer_keys.employer_name, employer_keys.employer_zip5

)

select cik, employer_name, employer_zip5, match_rule
from candidates
-- an employer that fits two startups equally well is dropped, as in the main matcher
qualify
    match_rule = min(match_rule) over (partition by employer_name, employer_zip5)
    and count(*) over (partition by employer_name, employer_zip5, match_rule) = 1
