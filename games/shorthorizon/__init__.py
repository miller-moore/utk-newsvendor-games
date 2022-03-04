from typing import Any, Dict, List
from uuid import uuid4

from .constants import C
from .models import Group, Player, Subsession
from .pages import page_sequence
from .treatment import Treatment, UnitCosts
from .util import get_time, initialize_game_history, is_practice_round


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        hydrate_participant(player)


def hydrate_participant(player: "Player", **kwargs) -> None:

    if not "uuid" in player.participant.vars:
        treatment: Treatment = player.participant.vars.get("treatment", Treatment.choose())
        _ = treatment.get_demand_rvs()  # initializes treatment._demand_rvs

        player.participant.uuid = player.participant.vars.get("uuid", str(uuid4()))
        player.participant.starttime = get_time()
        player.participant.is_planner = player.participant.vars.get("is_planner", player.field_maybe_none("is_planner"))
        player.participant.gender_identity = player.participant.vars.get(
            "gender_identity", player.field_maybe_none("gender_identity")
        )
        player.participant.does_consent = player.participant.vars.get("does_consent", player.field_maybe_none("does_consent"))
        player.participant.unit_costs = UnitCosts.from_treatment(treatment)
        player.participant.stock_units = 0
        player.participant.treatment = player.participant.vars.get("treatment", Treatment.choose())
        player.participant.history = initialize_game_history(is_practice=is_practice_round(player.round_number))
        player.participant.practice_results = []
        player.participant.game_results = []
        player.participant.payoff_round = player.field_maybe_none("payoff_round") or treatment.get_payoff_round()
