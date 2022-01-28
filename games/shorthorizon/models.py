import random
from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid4

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models, widgets
from otree.currency import Currency
from otree.models.participant import Participant
from otree.templating import filters

from .constants import C
from .treatment import Treatment, UnitCosts
from .util import get_game_number, get_game_rounds, get_round_in_game, get_time

# https://stackoverflow.com/a/12028864
# from django import template
# register = template.Library()


@filters.register("type")
def _type(value):
    return type(value)


@filters.register("len")
def _len(value):
    try:
        return len(value)
    except:
        return 0 if not value else 1


@filters.register
def isiterable(value):
    return isinstance(value, Iterable)


@filters.register
def add(value, other=0):
    try:
        if int(value) == value and int(other) == other:
            return int(value + other)
    except:
        pass
    try:
        return float(value) + float(other)
    except:
        pass
    try:
        return value + other
    except:
        pass
    return ""


def hydrate_participant(player: "Player", **kwargs) -> None:

    if not "uuid" in player.participant.vars:
        uuid = player.participant.vars.get("uuid", str(uuid4()))
        treatment: Treatment = player.participant.vars.get("treatment", Treatment.choose())
        unit_costs: UnitCosts = treatment.get_unit_costs()
        _ = treatment.get_demand_rvs()  # initializes treatment._demand_rvs
        is_planner = player.participant.vars.get("is_planner", player.field_maybe_none("is_planner"))
        game_number = get_game_number(player.round_number)
        round_in_game = get_round_in_game(player.round_number)
        game_rounds = get_game_rounds(player.round_number)

        player.participant.uuid = uuid
        player.participant.starttime = get_time()
        player.participant.is_planner = is_planner
        player.participant.unit_costs = unit_costs
        player.participant.stock_units = 0
        player.participant.treatment = treatment
        player.participant.history = initialize_game_history()
        player.participant.game_results = []
        player.participant.payoff_round = player.field_maybe_none("payoff_round") or treatment.get_payoff_round()


def initialize_game_history() -> List[Dict[str, Any]]:
    return [
        dict(
            period=i + 1,
            ou=None,
            du=None,
            su=None,
            ooq=None,
            revenue=None,
            cost=None,
            profit=None,
            cumulative_profit=None,
        )
        for i in range(C.ROUNDS_PER_GAME)
    ]


class Subsession(BaseSubsession):
    @staticmethod
    def creating_session(subsession: BaseSubsession):
        for player in subsession.get_players():
            hydrate_participant(player)

    # def vars_for_admin_report(self):
    #     """See https://otree.readthedocs.io/en/self/admin.html#customizing-the-admin-interface-admin-reports"""
    #     payoffs = sorted([p.payoff for p in self.get_players()])
    #     return dict(payoffs=payoffs)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # identifiers
    uuid = models.StringField()
    starttime = models.FloatField(min=get_time())
    endtime = models.FloatField(min=get_time())
    treatment = models.IntegerField(min=1)

    # Welcome.html form fields
    is_planner = models.BooleanField(
        widget=widgets.RadioSelectHorizontal(),
        label="""Are you presently either a Junior or Senior undergraduate or graduate student studying Supply Chain Management or another related field?""",
    )

    # player data
    game_number = models.IntegerField(min=1, initial=1)
    period_number = models.IntegerField(min=1, initial=1)

    # demand units, stock units, & order units (see Decide.html)
    du = models.IntegerField(min=0)
    su = models.IntegerField(min=0, initial=0)
    ou = models.IntegerField(min=0, max=1000, label="How many units will you order?")  # Decide.html

    # Optimal order quantity (see treatment.py)
    ooq = models.IntegerField(min=0)

    # Unit prices: retail price (revenue), wholesale price (cost), salvage price (cost)
    rcpu = models.CurrencyField()
    wcpu = models.CurrencyField()
    scpu = models.CurrencyField()

    # NOTE: revenue, cost, and profit fields are calculated in method `Decide.before_next_page` (pages.py:238)
    revenue = models.CurrencyField(initial=0)
    cost = models.CurrencyField(initial=0)
    profit = models.CurrencyField(initial=0)

    payoff_round = models.IntegerField()

    # final questions
    q1 = models.LongStringField(label="How did your decisions change between the two games?")
    q2 = models.LongStringField(label="How did your decisions change after the disruption?")
