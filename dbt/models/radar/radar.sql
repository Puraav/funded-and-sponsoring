-- The radar: recently funded Bay Area startups, scored 0 to 100 by H-1B filing history.
--   40 points  H-1B filings in the 24 months before the raise (log scale, full marks at 50)
--   25 points  any of them for a software, data or product role
--   15 points  any of them at prevailing wage Level I or II (early-career)
--   20 points  amount raised: <$2M 5, $2-10M 10, $10-50M 15, $50M+ 20
with raises as (

    select * from {{ ref('int_recent_raises') }}

),

history as (

    select
        raises.accession,
        sum(months.lcas) as lcas_24m,
        sum(months.software_lcas) as software_lcas,
        sum(months.data_lcas) as data_lcas,
        sum(months.product_lcas) as product_lcas,
        sum(months.early_career_lcas) as early_career_lcas,
        min(months.month) as first_month
    from raises
    inner join {{ ref('int_recent_matches') }} as matches
        on raises.cik = matches.cik
    inner join {{ source('seed_cache', 'lca_employer_history') }} as months
        on matches.employer_name = months.employer_name
        and matches.employer_zip5 = months.employer_zip5
        and months.month >= date_trunc('month', raises.filing_date - interval 24 month)
        and months.month <= raises.filing_date
    group by raises.accession

),

scored as (

    select
        raises.*,
        coalesce(history.lcas_24m, 0) as lcas_24m,
        coalesce(history.software_lcas, 0) as software_lcas,
        coalesce(history.data_lcas, 0) as data_lcas,
        coalesce(history.product_lcas, 0) as product_lcas,
        coalesce(history.early_career_lcas, 0) as early_career_lcas,
        history.first_month,
        40 * least(1.0, ln(1 + coalesce(history.lcas_24m, 0)) / ln(51)) as history_points,
        case
            when coalesce(history.software_lcas + history.data_lcas + history.product_lcas, 0) > 0
                then 25
            else 0
        end as tech_points,
        case when coalesce(history.early_career_lcas, 0) > 0 then 15 else 0 end as early_points,
        case raises.round_bin
            when '<$2M' then 5
            when '$2–10M' then 10
            when '$10–50M' then 15
            when '$50M+' then 20
            else 0
        end as raise_points
    from raises
    left join history
        on raises.accession = history.accession

)

select
    row_number() over (
        order by
            history_points + tech_points + early_points + raise_points desc,
            lcas_24m desc,
            amount_sold desc nulls last,
            accession
    ) as rank,
    accession,
    cik,
    company,
    city,
    county_name,
    industry,
    filing_date,
    amount_sold,
    round_bin,
    officers,
    cast(round(history_points + tech_points + early_points + raise_points) as integer) as score,
    cast(lcas_24m as integer) as lcas_24m,
    cast(software_lcas as integer) as software_lcas,
    cast(data_lcas as integer) as data_lcas,
    cast(product_lcas as integer) as product_lcas,
    cast(early_career_lcas as integer) as early_career_lcas,
    case
        when lcas_24m = 0 then 'No H-1B filings found in the last 24 months.'
        else concat_ws(
            ', ',
            lcas_24m || ' H-1B filing' || case when lcas_24m = 1 then '' else 's' end
            || ' since ' || strftime(first_month, '%b %Y'),
            case when software_lcas > 0 then software_lcas || ' for software roles' end,
            case when data_lcas > 0 then data_lcas || ' for data roles' end,
            case when product_lcas > 0 then product_lcas || ' for product roles' end,
            case when early_career_lcas > 0 then early_career_lcas || ' early-career' end
        ) || '.'
    end as reasons,
    'https://www.sec.gov/Archives/edgar/data/' || cast(cast(cik as bigint) as varchar) || '/'
    || replace(accession, '-', '') || '/' as sec_url
from scored
