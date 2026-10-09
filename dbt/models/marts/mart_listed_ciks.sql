-- Companies that carried an SEC industry (SIC) code on any Form D: SEC registrants, in
-- practice listed companies. Exported to data/seed_cache for the radar.
select distinct issuers.cik
from {{ ref('stg_formd_submissions') }} as submissions
inner join {{ ref('stg_formd_issuers') }} as issuers
    on submissions.accession_number = issuers.accession_number
    and issuers.is_primary_issuer
where submissions.sic_code is not null
