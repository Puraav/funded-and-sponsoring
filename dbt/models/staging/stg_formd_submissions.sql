select
    trim("ACCESSIONNUMBER") as accession_number,
    cast("FILING_DATE" as date) as filing_date,
    trim("SUBMISSIONTYPE") as submission_type,
    trim("TESTORLIVE") as test_or_live,
    quarter as source_quarter
from {{ source('formd', 'formdsubmission') }}
