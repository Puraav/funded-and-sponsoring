-- One row per distinct name and ZIP on each side of the match, with its matching key.
with formd as (

    select distinct
        'formd' as source,
        cik,
        company as entity_name,
        company as matched_on,
        zip5,
        'CA' as state
    from {{ ref('int_bay_area_raises') }}

),

lca_employers as (

    select distinct employer_name, trade_name_dba, employer_zip5, employer_state
    from {{ ref('int_lca_h1b') }}
    where employer_zip5 is not null

),

-- an employer can be found under its legal name or its trade name ("doing business as")
lca as (

    select distinct
        'lca' as source,
        cast(null as varchar) as cik,
        employer_name as entity_name,
        employer_name as matched_on,
        employer_zip5 as zip5,
        employer_state as state
    from lca_employers

    union

    select distinct
        'lca' as source,
        cast(null as varchar) as cik,
        employer_name as entity_name,
        trade_name_dba as matched_on,
        employer_zip5 as zip5,
        employer_state as state
    from lca_employers
    where trade_name_dba is not null

),

keyed as (

    select *, {{ normalise_name('matched_on') }} as name_key
    from (
        select * from formd
        union all
        select * from lca
    )

)

select
    keyed.source,
    keyed.cik,
    keyed.entity_name,
    keyed.matched_on,
    keyed.zip5,
    keyed.state,
    keyed.name_key,
    split_part(keyed.name_key, ' ', 1) as first_token,
    left(keyed.zip5, 3) as zip3,
    (
        (keyed.name_key not like '% %' and length(keyed.name_key) <= 5)
        or keyed.name_key in (select name_key from {{ ref('generic_names') }})
    ) as is_generic
from keyed
where keyed.name_key is not null
