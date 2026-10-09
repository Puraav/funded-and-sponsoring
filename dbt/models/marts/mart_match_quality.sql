-- How many startups matched an H-1B employer, and how often a checked match was right.
with matches as (

    select * from {{ ref('int_matches') }}

),

labels as (

    select * from {{ ref('match_labels') }}

),

rule_names as (

    select *
    from (
        values
            (1, 'Same name, same ZIP'),
            (2, 'Same name, Bay Area'),
            (3, 'Same name, California'),
            (4, 'Similar name, same 3-digit ZIP')
    ) as rules (match_rule, rule_name)

),

by_rule as (

    select
        match_rule,
        any_value(tier) as tier,
        count(*) as pairs,
        count(distinct cik) as startups
    from matches
    group by match_rule

),

labels_by_rule as (

    select
        match_rule,
        count(*) as labelled,
        count(*) filter (where correct = 'y') as labelled_correct
    from labels
    where sample_type = 'matched'
    group by match_rule

),

totals as (

    select
        (select count(*) from {{ ref('dim_company') }}) as all_startups,
        (select count(distinct cik) from matches) as matched_startups,
        (select count(*) from matches) as pairs

)

select
    'overall' as scope,
    cast(null as integer) as match_rule,
    'All rules' as rule_name,
    cast(null as varchar) as tier,
    totals.pairs,
    totals.matched_startups as startups,
    totals.all_startups,
    totals.matched_startups / totals.all_startups as match_rate,
    (select count(*) from labels where sample_type = 'matched') as labelled,
    (select count(*) from labels where sample_type = 'matched' and correct = 'y')
        as labelled_correct,
    (select avg((correct = 'y')::int) from labels where sample_type = 'matched')
        as match_precision,
    (select count(*) from labels where sample_type = 'matched') < 30 as small_sample
from totals

union all

select
    'rule' as scope,
    by_rule.match_rule,
    rule_names.rule_name,
    by_rule.tier,
    by_rule.pairs,
    by_rule.startups,
    totals.all_startups,
    by_rule.startups / totals.all_startups as match_rate,
    coalesce(labels_by_rule.labelled, 0) as labelled,
    coalesce(labels_by_rule.labelled_correct, 0) as labelled_correct,
    labels_by_rule.labelled_correct / labels_by_rule.labelled as match_precision,
    coalesce(labels_by_rule.labelled, 0) < 30 as small_sample
from by_rule
cross join totals
inner join rule_names
    on by_rule.match_rule = rule_names.match_rule
left join labels_by_rule
    on by_rule.match_rule = labels_by_rule.match_rule

union all

-- unmatched startups that were checked: "correct" means leaving them unmatched was right
select
    'unmatched' as scope,
    cast(null as integer) as match_rule,
    'No match' as rule_name,
    cast(null as varchar) as tier,
    0 as pairs,
    totals.all_startups - totals.matched_startups as startups,
    totals.all_startups,
    (totals.all_startups - totals.matched_startups) / totals.all_startups as match_rate,
    (select count(*) from labels where sample_type = 'unmatched') as labelled,
    (select count(*) from labels where sample_type = 'unmatched' and correct = 'y')
        as labelled_correct,
    (select avg((correct = 'y')::int) from labels where sample_type = 'unmatched')
        as match_precision,
    (select count(*) from labels where sample_type = 'unmatched') < 30 as small_sample
from totals
