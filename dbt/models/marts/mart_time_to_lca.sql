-- Days from the Form D filing to the first H-1B filing after it (within 12 months),
-- for raises with a full year of follow-up. One row per histogram bucket; the summary
-- columns repeat on every row.
with sponsored as (

    select days_to_first_lca
    from {{ ref('fct_raises') }}
    where has_full_followup and sponsored_after

),

summary as (

    select
        count(*) as n,
        median(days_to_first_lca) as median_days,
        quantile_cont(days_to_first_lca, 0.25) as p25_days,
        quantile_cont(days_to_first_lca, 0.75) as p75_days
    from sponsored

),

buckets as (

    select *
    from (
        values
            (1, '0–30', 0, 30),
            (2, '31–60', 31, 60),
            (3, '61–90', 61, 90),
            (4, '91–180', 91, 180),
            (5, '181–270', 181, 270),
            (6, '271–366', 271, 366)
    ) as b (bucket_order, bucket, low_days, high_days)

)

select
    buckets.bucket_order,
    buckets.bucket,
    buckets.low_days,
    buckets.high_days,
    count(sponsored.days_to_first_lca) as raises,
    count(sponsored.days_to_first_lca) / any_value(summary.n) as share,
    any_value(summary.n) as n,
    any_value(summary.median_days) as median_days,
    any_value(summary.p25_days) as p25_days,
    any_value(summary.p75_days) as p75_days,
    any_value(summary.n) < 30 as small_sample
from buckets
cross join summary
left join sponsored
    on sponsored.days_to_first_lca between buckets.low_days and buckets.high_days
group by buckets.bucket_order, buckets.bucket, buckets.low_days, buckets.high_days
