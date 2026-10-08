-- No startup raise may carry a name that matches a fund or SPV pattern.
select raises.accession, raises.company
from {{ ref('int_bay_area_raises') }} as raises
where {{ is_fund_name('raises.company') }}
