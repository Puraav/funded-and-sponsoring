-- What startups file for after raising: counts and median pay by role group and wage level.
-- wage_level 'All' is the total for the role group.
with lcas as (

    select * from {{ ref('int_post_raise_lcas') }}

),

total as (

    select count(*) as all_lcas from lcas

)

select
    lcas.role_group,
    'All' as wage_level,
    count(*) as n,
    count(*) / any_value(total.all_lcas) as share_of_lcas,
    median(lcas.annual_wage) as median_wage,
    count(*) < 30 as small_sample
from lcas
cross join total
group by lcas.role_group

union all

select
    role_group,
    pw_wage_level as wage_level,
    count(*) as n,
    cast(null as double) as share_of_lcas,
    median(annual_wage) as median_wage,
    count(*) < 30 as small_sample
from lcas
where pw_wage_level is not null
group by role_group, pw_wage_level
