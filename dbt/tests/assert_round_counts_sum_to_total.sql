-- The raises counted by round must add up to the raises behind the headline rate.
select by_round.total, headline.n
from (select sum(n) as total from {{ ref('mart_by_round') }}) as by_round
cross join (select n from {{ ref('mart_sponsor_rate') }} where metric = 'any') as headline
where by_round.total != headline.n
