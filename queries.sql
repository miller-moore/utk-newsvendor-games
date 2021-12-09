select pp.id, pl.participant_id, pp.code, time_started_utc, pl.payoff_round, pp.payoff, visited, _last_request_timestamp
from otree_participant pp
left join (
  select distinct participant_id, payoff_round
  from disruption_player
  where payoff_round is not null
) pl on pp.id = pl.participant_id
where code = (select code from otree_participant order by _last_request_timestamp desc limit 1) ;

