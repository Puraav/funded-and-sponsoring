-- Executive officers and directors named on each startup's latest Form D (name and role only).
with latest_raise as (

    select cik, accession
    from {{ ref('int_bay_area_raises') }}
    qualify row_number() over (partition by cik order by filing_date desc, accession desc) = 1

)

select
    latest_raise.cik,
    people.person_seq,
    trim(concat_ws(' ', people.first_name, people.middle_name, people.last_name)) as person_name,
    concat_ws(', ', people.relationship_1, people.relationship_2, people.relationship_3)
        as relationships
from latest_raise
inner join {{ ref('stg_formd_people') }} as people
    on latest_raise.accession = people.accession_number
where 'Executive Officer' in (
    people.relationship_1, people.relationship_2, people.relationship_3
)
