-- Every certified H-1B LCA filed by an employer that matched a startup: the sponsoring events.
select
    lca.case_number,
    matches.cik,
    matches.tier,
    matches.match_rule,
    lca.event_date,
    lca.received_date,
    lca.decision_date,
    lca.employer_name,
    lca.employer_zip5,
    lca.worksite_city,
    lca.worksite_state,
    lca.job_title,
    lca.soc_code,
    lca.soc_title,
    lca.role_group,
    lca.pw_wage_level,
    lca.annual_wage,
    lca.is_new_hire,
    lca.total_worker_positions
from {{ ref('int_lca_h1b') }} as lca
inner join {{ ref('int_matches') }} as matches
    on lca.employer_name = matches.employer_name
    and lca.employer_zip5 = matches.employer_zip5
