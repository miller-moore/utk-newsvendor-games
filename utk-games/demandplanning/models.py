from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid4

from otree.api import (BaseConstants, BaseGroup, BasePlayer, BaseSubsession,
                       Currency, models, widgets)
from otree.constants import BaseConstantsMeta
from otree.templating import filters
from rich import print

from .constants import (ALLOW_DISRUPTION, APP_DIR, APP_NAME, GAMES, ROUNDS,
                        RVS_SIZE)
from .treatment import Treatment, UnitCosts
from .util import (get_game_number, get_game_rounds,
                   get_includable_template_path, get_optimal_order_quantity,
                   get_page_name, get_round_in_game, get_settings, get_time)

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


# Hack to allow settattr on Constants at runtime
orig_constants_meta_setattr = BaseConstantsMeta.__setattr__
delattr(BaseConstantsMeta, "__setattr__")


class ConstantsBase(BaseConstants, metaclass=BaseConstantsMeta):
    pass


class Constants(ConstantsBase):
    # otree constants
    name_in_url = APP_NAME
    num_rounds = GAMES * ROUNDS
    players_per_group = None
    endowment = Currency(0)
    instructions_template = None

    # custom constants
    num_games = GAMES
    rounds_per_game = ROUNDS
    app_name = APP_DIR.name
    authors = [
        "Anne Dohmen, University of Tennessee - Knoxville, Department of Supply Chain Management",
        "Miller Moore, University of Tennessee - Knoxville, Department of Business Analytics & Statistics",
    ]
    static_asset_prefix = str("/" / Path(APP_NAME))  # TODO: append "/static" ?

    allow_disruption = ALLOW_DISRUPTION
    rvs_size = RVS_SIZE

    # paths for templates used in include tags, e.g., {{ include "demandplanning/style.html" }} or {{ include Constants.style_template }}
    style_template = get_includable_template_path("style.html")
    scripts_template = get_includable_template_path("scripts.html")
    sections_template = get_includable_template_path("sections.html")


ConstantsBase.__setattr__ = orig_constants_meta_setattr


def hydrate_participant(player: "Player", **kwargs) -> None:

    if not "uuid" in player.participant.vars:
        uuid = player.participant.vars.get("uuid", str(uuid4()))
        print(f"[yellow]hydrate_participant: Round {player.round_number}: creating session for participant {uuid}[/]")

        treatment: Treatment = player.participant.vars.get("treatment", Treatment.choose())
        unit_costs: UnitCosts = treatment.get_unit_costs()
        demand_rvs = player.participant.vars.get("demand_rvs", treatment.get_demand_rvs(Constants.rvs_size))
        is_planner = player.participant.vars.get("is_planner", player.field_maybe_none("is_planner"))
        years_as_planner = player.participant.vars.get("years_as_planner", player.field_maybe_none("years_as_planner"))
        company_name = player.participant.vars.get("company_name", player.field_maybe_none("company_name"))
        does_consent = player.participant.vars.get("does_consent", player.field_maybe_none("does_consent"))
        game_number = get_game_number(player.round_number)
        round_in_game = get_round_in_game(player.round_number)
        game_rounds = get_game_rounds(player.round_number)

        player.participant.uuid = uuid
        player.participant.starttime = get_time()
        player.participant.is_planner = is_planner
        player.participant.years_as_planner = years_as_planner
        player.participant.company_name = company_name
        player.participant.does_consent = does_consent
        player.participant.unit_costs = unit_costs
        player.participant.stock_units = 0
        player.participant.treatment = treatment
        player.participant.demand_rvs = demand_rvs
        player.participant.history = initialize_game_history()
        player.participant.game_results = []


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
        for i in range(ROUNDS)
    ]


class Subsession(BaseSubsession):
    @staticmethod
    def creating_session(subsession: BaseSubsession):
        for player in subsession.get_players():
            hydrate_participant(player)

    def vars_for_admin_report(self):
        """See https://otree.readthedocs.io/en/self/admin.html#customizing-the-admin-interface-admin-reports"""
        payoffs = sorted([p.payoff for p in self.get_players()])
        return dict(payoffs=payoffs)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # identifiers
    uuid = models.StringField()
    starttime = models.FloatField(min=get_time())
    endtime = models.FloatField(min=get_time())

    # participant data
    treatment = models.LongStringField()
    # participant Welcome formfields
    is_planner = models.BooleanField(widget=widgets.RadioSelectHorizontal(), label="Are you presently employed as a planner?")
    years_as_planner = models.IntegerField(
        label="How many years in your career have you held the role of planner (rounded to the nearest year)?"
    )
    company_name = models.StringField(
        label="What is the name of the company your currently work for?",
    )
    does_consent = models.BooleanField(
        widget=widgets.CheckboxInput(),
        label="By checking this box, you consent to participate in this study. You understand that all data will be kept confidential by the researcher. Your personal information will not be stored in backend databases. You are free to withdraw at any time without giving a reason.",
    )

    # player data
    game_number = models.IntegerField(min=1, initial=1)
    period_number = models.IntegerField(min=1, initial=1)

    # stock units, order units, demand units
    su = models.IntegerField(min=0, initial=0)
    ou = models.IntegerField(min=0)  # formfield 'ou'
    du = models.IntegerField(min=0)
    ooq = models.IntegerField(min=0)

    # retail cost per unit (revenue), wholesale cost per unit (cost), holding cost per unit (cost)
    rcpu = models.CurrencyField()
    wcpu = models.CurrencyField()
    hcpu = models.CurrencyField()

    # revenue = rcpu * du
    # cost = wcpu * ou + hcpu * su
    # profit = revenue - cost
    revenue = models.CurrencyField(initial=0)
    cost = models.CurrencyField(initial=0)
    profit = models.CurrencyField(initial=0)


def custom_export(players: Iterable[Player]):
    """See https://otree.readthedocs.io/en/self/admin.html#custom-data-exports"""
    yield ["session", "participant_code", "round_number", "id_in_group", "payoff"]
    for p in players:
        yield [p.session.code, p.participant.code, p.round_number, p.id_in_group, p.payoff]
