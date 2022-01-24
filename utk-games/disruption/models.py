from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid4

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models, widgets
from otree.templating import filters

from .constants import Constants
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
def add(value, other):
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
        years_as_planner = player.participant.vars.get("years_as_planner", player.field_maybe_none("years_as_planner"))
        does_consent = player.participant.vars.get("does_consent", player.field_maybe_none("does_consent"))
        prolific_id = player.participant.vars.get("prolific_id", player.field_maybe_none("prolific_id"))
        game_number = get_game_number(player.round_number)
        round_in_game = get_round_in_game(player.round_number)
        game_rounds = get_game_rounds(player.round_number)

        player.participant.uuid = uuid
        player.participant.starttime = get_time()
        player.participant.is_planner = is_planner
        player.participant.years_as_planner = years_as_planner
        player.participant.does_consent = does_consent
        player.participant.prolific_id = prolific_id
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
            su_before=0 if i == 0 else None,
            su_after=None,
            ooq=None,
            revenue=None,
            cost=None,
            profit=None,
            cumulative_profit=None,
        )
        for i in range(Constants.rounds_per_game)
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

    # participant data
    treatment = models.IntegerField(min=1)

    # participant Welcome formfields
    is_planner = models.BooleanField(
        widget=widgets.RadioSelectHorizontal(),
        # label="Are you presently employed as a planner?"
        label="Are you presently employed in a manufacturing and/or operations management role?",
    )
    years_as_planner = models.IntegerField(
        label="How many years experience do you have in a manufacturing/ operations management role?", min=0, max=70
    )
    does_consent = models.BooleanField(
        widget=widgets.CheckboxInput(),
        label="""By checking the button to the left you agree to participate in this survey.""",  # NOTE: new label (Jan 2022)
        # label="By checking this box, you consent to participate in this study. You understand that all data will be kept confidential by the researcher. Your personal information will not be stored in backend databases. You are free to withdraw at any time without giving a reason.", # NOTE: old label
    )
    prolific_id = models.StringField(  # NOTE: added (Jan 2022)
        label="Please type or copy/paste your Prolific ID here (e.g., 5b96601d3400a939db45dac9):",
    )
    # company_name = models.StringField( # NOTE: replaced by prolific_id (Jan 2022)
    #     label="What is the name of the company your currently work for?",
    # )

    # player data
    game_number = models.IntegerField(min=1, initial=1)
    period_number = models.IntegerField(min=1, initial=1)

    # stock units, order units, demand units
    su = models.IntegerField(min=0, initial=0)
    ou = models.IntegerField(min=0, max=1000)  # formfield 'ou'
    du = models.IntegerField(min=0)
    ooq = models.IntegerField(min=0)

    # retail cost per unit (revenue), wholesale cost per unit (cost), holding cost per unit (cost)
    rcpu = models.CurrencyField()
    wcpu = models.CurrencyField()
    hcpu = models.CurrencyField()
    # scpu = models.CurrencyField()

    # revenue = rcpu * du
    # cost = wcpu * ou + hcpu * su
    # profit = revenue - cost
    revenue = models.CurrencyField(initial=0)
    cost = models.CurrencyField(initial=0)
    profit = models.CurrencyField(initial=0)

    payoff_round = models.IntegerField()

    # final questions
    q1 = models.LongStringField(label="How did your decisions change between the two games?")
    q2 = models.LongStringField(label="How did your decisions change after the disruption?")


# def custom_export(players: Iterable[Player]):
#     """See https://otree.readthedocs.io/en/self/admin.html#custom-data-exports"""
#     player_fields = [
#         "starttime",
#         "endtime",
#         "treatment",
#         "is_planner",
#         "years_as_planner",
#         "does_consent",
#         "prolific_id",
#         "game_number",
#         "period_number",
#         "su",
#         "ou",
#         "du",
#         "ooq",
#         "rcpu",
#         "wcpu",
#         "hcpu",
#         "revenue",
#         "cost",
#         "profit",
#         "payoff_round",
#         "payoff",
#     ]
#     yield ["id", "participant_code", *player_fields]

#     records = []
#     for p in players:
#         records.append([p.id, p.participant.code, *[getattr(p, name) for name in player_fields]])
#     records = sorted(records)
#     for r in records:
#         yield r
