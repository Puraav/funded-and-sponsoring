select
    trim("ACCESSIONNUMBER") as accession_number,
    nullif(trim("INDUSTRYGROUPTYPE"), '') as industry_group,
    nullif(trim("INVESTMENTFUNDTYPE"), '') as investment_fund_type,
    lower(trim("ISAMENDMENT")) = 'true' as is_amendment,
    cast("SALE_DATE" as date) as first_sale_date,
    lower(trim("YETTOOCCUR")) = 'true' as sale_yet_to_occur,
    lower(trim("ISEQUITYTYPE")) = 'true' as is_equity,
    lower(trim("ISDEBTTYPE")) = 'true' as is_debt,
    lower(trim("ISPOOLEDINVESTMENTFUNDTYPE")) = 'true' as is_pooled_fund_interest,
    lower(trim("ISBUSINESSCOMBINATIONTRANS")) = 'true' as is_business_combination,
    nullif(trim("REVENUERANGE"), '') as revenue_range,
    -- "Indefinite" was already turned into null when the raw file was parsed
    cast("TOTALOFFERINGAMOUNT" as decimal(18, 2)) as amount_offered,
    cast("TOTALAMOUNTSOLD" as decimal(18, 2)) as amount_sold,
    try_cast(nullif(trim("TOTALNUMBERALREADYINVESTED"), '') as integer) as investor_count,
    quarter as source_quarter
from {{ source('formd', 'offering') }}
