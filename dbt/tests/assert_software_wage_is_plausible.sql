-- Catches wage-unit bugs: the median annual wage for Software roles worked in California
-- must sit between $110k and $230k.
select median(annual_wage) as median_software_wage_ca
from {{ ref('int_lca_h1b') }}
where role_group = 'Software'
    and worksite_state = 'CA'
having median(annual_wage) not between 110000 and 230000
