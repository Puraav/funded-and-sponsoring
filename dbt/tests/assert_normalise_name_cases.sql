-- Unit test for the normalise_name macro: every case in the name_cases seed must come out right.
select raw, expected, {{ normalise_name('raw') }} as got
from {{ ref('name_cases') }}
where {{ normalise_name('raw') }} is distinct from expected
