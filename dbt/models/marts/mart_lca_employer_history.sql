-- Certified H-1B LCAs per California employer per month. Exported to data/seed_cache so the
-- weekly radar can score new raises without the full LCA data.
select
    employer_name,
    trade_name_dba,
    employer_zip5,
    cast(date_trunc('month', event_date) as date) as month,
    count(*) as lcas,
    count(*) filter (where role_group = 'Software') as software_lcas,
    count(*) filter (where role_group = 'Data') as data_lcas,
    count(*) filter (where role_group = 'Product') as product_lcas,
    count(*) filter (where pw_wage_level in ('I', 'II')) as early_career_lcas
from {{ ref('int_lca_h1b') }}
where employer_state = 'CA'
    and employer_zip5 is not null
group by all
