-- Every matching rule in use must have been checked by hand and be right at least 90% of
-- the time. A rule that fails must be tightened or dropped.
select match_rule, rule_name, labelled, match_precision
from {{ ref('mart_match_quality') }}
where scope = 'rule'
    and (labelled = 0 or match_precision < 0.90)
