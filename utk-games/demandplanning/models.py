import json
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from otree.api import BaseConstants, BaseGroup, BasePlayer, BaseSubsession
from otree.api import Currency
from otree.api import Currency as c
from otree.api import currency_range, models, widgets
from otree.constants import BaseConstantsMeta
from otree.models import subsession

from . import util
from .treatment import Treatment, UnitCosts

GAMES = 2
ROUNDS = 3
RVS_SIZE = int(1e5)
APP_DIR = Path(__file__).resolve().parent
APP_NAME = APP_DIR.name
STATIC_DIR = APP_DIR / "static"
INCLUDES_DIR = APP_DIR / "includes"
ALLOW_DISRUPTION = False

for dr in [STATIC_DIR, INCLUDES_DIR]:
    dr.mkdir(parents=True, exist_ok=True)
del dr


def rounds_for_game(game_number: int) -> List[int]:
    last_round = ROUNDS * game_number + 1
    first_round = last_round - ROUNDS
    return list(range(first_round, last_round))


def game_of_round(round_number: int) -> int:
    return ((round_number - 1) - (round_number - 1) % ROUNDS) // ROUNDS + 1


def round_of_game(round_number: int) -> int:
    game_number = game_of_round(round_number)
    return round_number - (game_number - 1) * ROUNDS


def is_end_of_game(round_number: int) -> bool:
    game_number = game_of_round(round_number)
    return round_number == game_number * ROUNDS


def should_disrupt_next_round(player: "Player") -> bool:
    if player.round_number == 1:
        return False

    treatment = player.participant.vars.get("treatment", None)
    assert treatment, f"no 'treatment' attribute exists on player.participant"

    game_number = game_of_round(player.round_number)
    next_game_round = round_of_game(player.round_number)

    conditions = [
        treatment.disrupt_is_true() and game_number == 1 and next_game_round == int(3 / 4 * ROUNDS),
        game_number == 2 and next_game_round == int(1 / 4 * ROUNDS),
    ]
    return any(conditions)


def django_include_template(html_filename: str) -> str:
    """Return a string of the path to a template file for django include expressions, e.g., {{ include "my-html-include-template" }}."""
    assert html_filename.endswith(".html"), f"""html_filename does not endwith {".html"!r}"""

    # strict file path (must exist)
    filepath = (APP_DIR / html_filename).resolve(strict=True)

    # return string for django include expression: {{ include "include_path" }}
    include_path = str(Path(APP_DIR.name) / filepath.name)
    return include_path


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
    app_name = APP_DIR.name
    authors = [
        "Anne Dohmen, University of Tennessee - Knoxville, Department of Supply Chain Management",
        "Miller Moore, University of Tennessee - Knoxville, Department of Business Analytics & Statistics",
    ]
    static_asset_prefix = str("/" / Path(APP_NAME))  # TODO: append "/static" ?

    # template paths for django include
    title_template = django_include_template("title.html")
    style_template = django_include_template("style.html")
    scripts_template = django_include_template("scripts.html")


ConstantsBase.__setattr__ = orig_constants_meta_setattr


class Subsession(BaseSubsession):
    def creating_session(self: BaseSubsession) -> None:
        # TODO: apply disruption to participant based on round_number

        print(f"Round number: {self.round_number}")
        print(f"Last round in game? {is_end_of_game(self.round_number)}")

        game_of_round = util.game_of_round(self.round_number, ROUNDS)
        if game_of_round > GAMES:
            raise ValueError(f"game number cannot be > {GAMES}: got {game_of_round}")

        if self.round_number == 1:
            settings = util.get_settings()
            print("Game settings: %s", str(settings.asdict()))

            # print(f"Initializing participant fields")
            # for player in self.get_players():
            #     treatment = Treatment.choose()
            #     starttime = util.get_time()
            #     unit_costs = treatment.get_unit_costs()
            #     demand_rvs = treatment.get_demand_rvs(RVS_SIZE)

            #     player.participant.treatment = treatment
            #     player.participant.starttime = starttime
            #     player.participant.stock_units = 0
            #     player.participant.unit_costs = unit_costs
            #     player.participant.demand_rvs = demand_rvs
            #     player.participant.round_results = []
            #     player.participant.game_results = []

            #     player.starttime = starttime
            #     player.endtime = None
            #     player.rcpu = unit_costs.rcpu
            #     player.wcpu = unit_costs.wcpu
            #     player.hcpu = unit_costs.hcpu
            #     player.su = 0
            #     player.ou = None
            #     player.du = None
            #     player.revenue = None
            #     player.cost = None
            #     player.profit = None

        # elif is_end_of_game(self.round_number):
        #     print(f"Resetting participant stock_units to zero for new game")
        #     for player in self.get_players():
        #         player.participant.stock_units = 0

        # elif is_disruption_round(self.round_number):
        #     pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # identifiers
    starttime = models.FloatField()
    endtime = models.FloatField()

    # stock units, order units, demand units
    su = models.IntegerField(min=0)
    ou = models.IntegerField(min=0)
    du = models.IntegerField(min=0)

    # retail cost per unit, wholesale cost per unit, holding cost per unit
    wcpu = models.CurrencyField()
    hcpu = models.CurrencyField()

    # retail cost (revenue) per unit
    rcpu = models.CurrencyField()

    # revenue = rcpu * du
    revenue = models.CurrencyField()

    # cost = wcpu * ou + hcpu * su
    cost = models.CurrencyField()

    # profit = revenue - cost
    profit = models.CurrencyField()
