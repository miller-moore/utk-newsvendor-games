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

APP_DIR = Path(__file__).resolve().parent
APP_NAME = APP_DIR.name
STATIC_DIR = APP_DIR / "static"
INCLUDES_DIR = APP_DIR / "includes"

for dr in [STATIC_DIR, INCLUDES_DIR]:
    dr.mkdir(parents=True, exist_ok=True)
del dr


GAMES = 2
ROUNDS = 3
RVS_SIZE = int(1e5)


def jinja2_include_path(html_filename: str) -> str:
    """Return a string of the path to a template file for jinja2 include expressions, e.g., {{ include "my-html-include-template" }}."""
    assert html_filename.endswith(".html"), f"""html_filename does not endwith {".html"!r}"""

    # strict file path (must exist)
    filepath = (APP_DIR / html_filename).resolve(strict=True)

    # return string for jinja2 include expression: {{ include "include_path" }}
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
    app_name = APP_DIR.name
    authors = [
        "Anne Dohmen, University of Tennessee - Knoxville, Department of Supply Chain Management",
        "Miller Moore, University of Tennessee - Knoxville, Department of Business Analytics & Statistics",
    ]
    static_asset_prefix = str("/" / Path(APP_NAME))  # TODO: append "/static" ?

    # template paths for jinja2 include
    style_template = jinja2_include_path("style.html")
    title_template = jinja2_include_path("title.html")
    game_number_template = jinja2_include_path("game_number.html")
    demand_distribution_chart_template = jinja2_include_path("demand_distribution_chart.html")
    display_card_template = jinja2_include_path("display_card.html")


ConstantsBase.__setattr__ = orig_constants_meta_setattr


def rounds_for_game(game_number: int) -> List[int]:
    last_round = ROUNDS * game_number + 1
    first_round = last_round - ROUNDS
    return list(range(first_round, last_round))


def game_of_round(round_number: int):
    return ((round_number - 1) - (round_number - 1) % ROUNDS) // ROUNDS + 1


def is_end_of_game(round_number: int):
    game_number = game_of_round(round_number)
    return round_number == game_number * ROUNDS


def is_disruption_round(round_number: int):
    if game_of_round(round_number) == 2:
        return True
    return False


game_number = None


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
            #     treatment = Treatment()
            #     player.participant.treatment = treatment
            #     player.participant.starttime = util.get_time()
            #     player.participant.endtime = None
            #     player.participant.unit_costs = treatment.get_unit_costs()
            #     player.participant.demand_rvs = treatment.get_demand_rvs(RVS_SIZE)
            #     player.participant.stock_units = 0
            #     player.participant.game_results = []

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
    su = models.FloatField(min=0)
    ou = models.FloatField(min=0)
    du = models.FloatField(min=0)

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
