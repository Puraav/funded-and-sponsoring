select
    trim("ACCESSIONNUMBER") as accession_number,
    try_cast("RELATEDPERSON_SEQ_KEY" as integer) as person_seq,
    nullif(trim("FIRSTNAME"), '') as first_name,
    nullif(trim("MIDDLENAME"), '') as middle_name,
    nullif(trim("LASTNAME"), '') as last_name,
    nullif(trim("RELATIONSHIP_1"), '') as relationship_1,
    nullif(trim("RELATIONSHIP_2"), '') as relationship_2,
    nullif(trim("RELATIONSHIP_3"), '') as relationship_3,
    quarter as source_quarter
from {{ source('formd', 'relatedpersons') }}
