-- Every startup-to-employer pair that passes one of the four rules, with its best rule.
-- Rule 1 is the strictest; a pair is kept at the first rule it passes.
with startups as (

    select * from {{ ref('int_name_keys') }} where source = 'formd'

),

employers as (

    select
        keys.*,
        zips.zip is not null as in_bay_area
    from {{ ref('int_name_keys') }} as keys
    left join {{ ref('bay_area_zips') }} as zips
        on keys.zip5 = zips.zip
    where keys.source = 'lca'

),

exact as (

    select
        startups.cik,
        employers.entity_name as employer_name,
        employers.zip5 as employer_zip5,
        case
            when startups.zip5 = employers.zip5 then 1
            when employers.in_bay_area then 2
            when employers.state = 'CA' then 3
        end as match_rule
    from startups
    inner join employers
        on startups.name_key = employers.name_key
    -- generic names (Nova, Apex, ...) only count in the very same ZIP code
    where startups.zip5 = employers.zip5
        or (not startups.is_generic and (employers.in_bay_area or employers.state = 'CA'))

),

fuzzy as (

    select
        startups.cik,
        employers.entity_name as employer_name,
        employers.zip5 as employer_zip5,
        4 as match_rule
    from startups
    inner join employers
        on startups.zip3 = employers.zip3
        and startups.first_token = employers.first_token
        and startups.name_key != employers.name_key
    where not startups.is_generic
        and jaro_winkler_similarity(startups.name_key, employers.name_key) >= 0.97

)

select
    cik,
    employer_name,
    employer_zip5,
    min(match_rule) as match_rule
from (
    select * from exact
    union all
    select * from fuzzy
)
group by cik, employer_name, employer_zip5
