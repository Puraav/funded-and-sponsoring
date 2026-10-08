select
    trim("ACCESSIONNUMBER") as accession_number,
    upper(trim("IS_PRIMARYISSUER_FLAG")) = 'YES' as is_primary_issuer,
    try_cast("ISSUER_SEQ_KEY" as integer) as issuer_seq,
    lpad(trim("CIK"), 10, '0') as cik,
    nullif(regexp_replace(trim("ENTITYNAME"), '\s+', ' ', 'g'), '') as entity_name,
    nullif(trim("STREET1"), '') as street1,
    nullif(trim("STREET2"), '') as street2,
    nullif(trim("CITY"), '') as city,
    nullif(upper(trim("STATEORCOUNTRY")), '') as state,
    nullif(trim("ZIPCODE"), '') as zipcode,
    case
        when regexp_matches(trim("ZIPCODE"), '^[0-9]{5}') then left(trim("ZIPCODE"), 5)
    end as zip5,
    nullif(trim("JURISDICTIONOFINC"), '') as jurisdiction_of_inc,
    nullif(trim("ENTITYTYPE"), '') as entity_type,
    nullif(trim("YEAROFINC_TIMESPAN_CHOICE"), '') as year_of_inc_timespan,
    try_cast(nullif(trim("YEAROFINC_VALUE_ENTERED"), '') as integer) as year_of_inc,
    quarter as source_quarter
from {{ source('formd', 'issuers') }}
