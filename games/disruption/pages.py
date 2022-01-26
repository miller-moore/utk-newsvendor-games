import os
import random
from collections import deque
from decimal import ROUND_HALF_UP, Decimal
from functools import wraps
from pathlib import Path
from threading import Thread
from typing import Any, Callable, Dict, Generator, List, Optional, Type, Union
from uuid import uuid4

import numpy as np
from otree.api import Currency, Page
from otree.lookup import PageLookup, _get_session_lookups
from otree.models import Participant
from otree.session import Session

from .constants import C
from .formvalidation import (default_error_message,
                             register_form_field_validator)
from .models import Player, initialize_game_history
from .treatment import Distribution, Treatment
from .util import (as_static_path, get_app_name, get_game_number,
                   get_game_rounds, get_optimal_order_quantity, get_page_name,
                   get_room_display_name, get_room_name, get_round_in_game,
                   get_time, is_absolute_final_round, is_disruption_next_round,
                   is_disruption_this_round, is_game_over)

from common.colors import COLORS  # isort:skip
from common.google_image_downloader import GoogleImageDownloader  # isort:skip


# fetch smokey images in the background
smokey_the_dog_image_fetcher = GoogleImageDownloader(
    query="utk-smokey-the-dog", api_key=os.getenv("SERPAPI_KEY", None), download_directory=C.STATIC_DIR, max_count=1000
)


@register_form_field_validator(form_field="is_planner", expect_type=bool)
def validate_is_planner(is_planner: bool) -> Optional[str]:
    # if is_planner is False:
    #     return f"""Must be True."""
    return


@register_form_field_validator(form_field="years_as_planner", expect_type=int)
def validate_years_as_planner(years_as_planner: int) -> Optional[str]:
    if years_as_planner < 0:
        return f"""Years in role must be >= 0."""
    return


@register_form_field_validator(form_field="prolific_id", expect_type=str)
def validate_prolific_id(prolific_id: str) -> Optional[str]:
    import re

    chars = 24
    if not re.findall(f"[a-zA-Z0-9]{ {chars} }", str(prolific_id)):
        return f"""Prolific ID must be a string with exactly {chars} alphanumeric characters (i.e., a-z, A-Z, and 0-9; special characters are not allowed)."""
    return


@register_form_field_validator(form_field="does_consent", expect_type=bool)
def validate_does_consent(does_consent: bool) -> Optional[str]:
    if does_consent is False:
        return f"""Must consent."""
    return


class DisruptionPage(Page):

    error_message = staticmethod(default_error_message)

    @staticmethod
    def vars_for_template(player: Player) -> dict:

        from otree.settings import (LANGUAGE_CODE, LANGUAGE_CODE_ISO,
                                    REAL_WORLD_CURRENCY_CODE,
                                    REAL_WORLD_CURRENCY_DECIMAL_PLACES)

        # import importlib
        # from . import treatment as disruption_treatment
        # treatment_module = importlib.reload(disruption_treatment)

        treatment: Treatment = player.participant.vars.get("treatment", None)
        distribution: Distribution = treatment.get_distribution()

        try:
            smokey_img_file = as_static_path(random.choice(smokey_the_dog_image_fetcher.smokey_images))
        except:
            smokey_img_file = None

        _vars = dict(
            language_code=LANGUAGE_CODE,
            real_world_currency_code=REAL_WORLD_CURRENCY_CODE,
            real_world_currency_decimal_places=REAL_WORLD_CURRENCY_DECIMAL_PLACES,
            smokey_img_file=smokey_img_file,
            colors=COLORS.copy(),
            games=C.NUM_GAMES,
            rounds=C.ROUNDS_PER_GAME,
            room_name=get_room_name(player),
            room_display_name=get_room_display_name(player),
            allow_disruption=C.ALLOW_DISRUPTION,
            page_name=get_page_name(player),
            app_name=get_app_name(player),
            round_number=player.round_number,
            game_number=player.game_number,  # game_number,
            game_round=player.period_number,  # game_round,
            period_number=player.period_number,  # game_round,
            session_code=player.session.code,
            participant_code=player.participant.code,
            variance_choice=treatment.variance_choice if treatment else None,
            disruption_choice=treatment.disruption_choice if treatment else None,
            disruption_round=C.DISRUPTION_ROUND_IN_GAMES.get(player.game_number, None)
            if treatment.disruption_choice and player.game_number == 1
            else None,
            distribution_png=as_static_path(treatment.get_distribution_plot()),
            # NOTE: snapshot_disruption_1 is displayed on Page 'disruption/Disruption.html'
            snapshot_disruption_1=as_static_path(Path(C.STATIC_DIR).joinpath("snapshot-disruption-1.png")),
            # NOTE: snapshot_instructions_1, snapshot_instructions_2, & snapshot_instructions_3 are all displayed on Page 'disruption/Instructions3.html'
            snapshot_instructions_1=as_static_path(Path(C.STATIC_DIR).joinpath("snapshot-instructions-1.png")),
            snapshot_instructions_2=as_static_path(Path(C.STATIC_DIR).joinpath("snapshot-instructions-2.png")),
            snapshot_instructions_3=as_static_path(Path(C.STATIC_DIR).joinpath("snapshot-instructions-3.png")),
            is_pilot_test=player.session.config.get("is_pilot_test", False),
            is_disrupted=treatment.is_disrupted(),
            is_disruption_this_round=is_disruption_this_round(player),
            is_disruption_next_round=is_disruption_next_round(player),
            is_game_over=is_game_over(player.round_number),
            is_absolute_final_round=is_absolute_final_round(player.round_number),
            uuid=player.field_maybe_none("uuid"),
            starttime=player.field_maybe_none("starttime"),
            endtime=player.field_maybe_none("endtime"),
            is_planner=player.field_maybe_none("is_planner"),
            years_as_planner=player.field_maybe_none("years_as_planner"),
            does_consent=player.field_maybe_none("does_consent"),
            prolific_id=player.field_maybe_none("prolific_id"),
            su=player.field_maybe_none("su"),
            ou=player.field_maybe_none("ou"),
            du=player.field_maybe_none("du"),
            ooq=player.field_maybe_none("ooq"),
            rcpu=player.field_maybe_none("rcpu"),
            wcpu=player.field_maybe_none("wcpu"),
            hcpu=player.field_maybe_none("hcpu"),
            revenue=player.field_maybe_none("revenue"),
            cost=player.field_maybe_none("cost"),
            profit=player.field_maybe_none("profit"),
            history=player.participant.vars.get("history", None),
            game_results=player.participant.vars.get("game_results", None),
            payoff_round=player.participant.vars.get("payoff_round", None),
            payoff=player.participant.vars.get("payoff", None),
            treatment=treatment.idx,
            mu=distribution.mu if not treatment.is_disrupted() else distribution.mu_disrupted,
            sigma=distribution.sigma if not treatment.is_disrupted() else distribution.sigma_disrupted,
        )

        # make Currency (Decimal) objects json serializable
        for ckey in ["rcpu", "wcpu", "hcpu", "revenue", "cost", "profit"]:
            val = _vars.get(ckey)
            _vars.update({ckey: float(val) if val else None})

        return _vars

    @staticmethod
    def js_vars(player: Player) -> dict:
        _vars = DisruptionPage.vars_for_template(player).copy()
        treatment = player.participant.treatment
        _vars.update(demand_rvs=treatment.get_demand_rvs())
        return _vars


class HydratePlayer(DisruptionPage):

    timeout_seconds = 0

    @staticmethod
    def before_next_page(player: Player, **kwargs):
        """Hydrates player from participant. The participant is hydrated in `creating_subsession` (in models.py)."""
        player.uuid = player.participant.uuid
        player.starttime = get_time()
        player.endtime = None
        player.treatment = player.participant.treatment.idx
        player.is_planner = player.participant.is_planner
        player.years_as_planner = player.participant.years_as_planner
        player.does_consent = player.participant.does_consent
        player.prolific_id = player.participant.prolific_id
        player.game_number = get_game_number(player.round_number)
        player.period_number = get_round_in_game(player.round_number)
        player.su = player.participant.stock_units
        player.ou = None
        player.du = None
        player.ooq = get_optimal_order_quantity(player)
        player.rcpu = player.participant.unit_costs.rcpu
        player.wcpu = player.participant.unit_costs.wcpu
        player.hcpu = player.participant.unit_costs.hcpu
        player.revenue = 0
        player.cost = 0
        player.profit = 0
        player.payoff_round = player.participant.payoff_round

        extras = dict(su=player.su, ooq=player.ooq, is_planner=player.field_maybe_none("is_planner"))
        print(
            f"hydrate_player: Round {player.round_number}: {get_page_name(player)} Page, Game {player.game_number} (ends on round {get_game_rounds(player.round_number)[-1]}), Period number: {player.period_number}, player extras: {extras}"
        )


class Welcome(DisruptionPage):
    form_model = "player"
    form_fields = ["is_planner", "years_as_planner", "does_consent", "prolific_id"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.is_planner = player.is_planner
        player.participant.years_as_planner = player.years_as_planner
        player.participant.does_consent = player.does_consent
        player.participant.prolific_id = player.prolific_id


class Instructions1(DisruptionPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Instructions2(DisruptionPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Instructions3(DisruptionPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Disruption(DisruptionPage):
    @staticmethod
    def is_displayed(player: Player):
        return is_disruption_this_round(player)

    @staticmethod
    def before_next_page(player: Player, **kwargs):
        if C.ALLOW_DISRUPTION:
            player.participant.treatment.disrupt()


class Decide(DisruptionPage):

    form_model = "player"
    form_fields = ["ou"]

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:

        # unit costs
        unit_costs = player.participant.unit_costs
        rcpu = float(unit_costs.rcpu)
        wcpu = float(unit_costs.wcpu)
        hcpu = float(unit_costs.hcpu)

        # Get demand units!
        # NOTE: not randomly means from pre-determined data
        du = player.participant.treatment.get_demand(randomly=False, player=player)

        # units availaboe
        su = player.participant.stock_units
        ou = player.ou

        # compute revenue, cost, profit
        if su + ou > du:
            cost = ou * wcpu + su * hcpu
            revenue = du * rcpu
        else:
            cost = ou * wcpu
            revenue = (su + ou) * rcpu
        profit = revenue - cost

        player.revenue = Currency(revenue)
        player.cost = Currency(cost)
        player.profit = Currency(profit)

        su_new = max(0, ou + su - du)
        player.su = su_new
        player.du = du

        # update participant fields

        # stock units
        player.participant.stock_units = su_new

        # cumulative profit
        first_round_in_game = get_game_rounds(player.round_number)[0]
        cumulative_profit = (
            sum(p.profit for p in player.in_rounds(first_round_in_game, player.round_number - 1)) + player.profit
        )

        # history
        idx = get_round_in_game(player.round_number) - 1
        hist = player.participant.history[idx]
        hist.update(
            ou=ou,
            du=du,
            su_before=su,
            su_after=su_new,
            ooq=player.ooq,
            revenue=float(revenue),
            cost=float(cost),
            profit=float(profit),
            cumulative_profit=float(cumulative_profit),
        )
        player.participant.history[idx] = hist

        if player.round_number == player.participant.payoff_round:
            player.payoff = Currency(min(1750, max(750, player.profit * 0.05)))
        else:
            player.payoff = Currency(0)


class Results(DisruptionPage):
    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:
        player.endtime = get_time()
        if is_game_over(player.round_number):
            # store game history & flush game state
            player.participant.game_results.append(player.participant.history)
            player.participant.history = initialize_game_history()
            player.participant.stock_units = 0
            player.participant.treatment.reset()


class FinalResults(DisruptionPage):
    @staticmethod
    def is_displayed(player: Player):
        return is_game_over(player.round_number)


class FinalQuestions(DisruptionPage):

    form_model = "player"
    form_fields = ["q1", "q2"]

    @staticmethod
    def is_displayed(player: Player):
        return is_absolute_final_round(player.round_number)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if is_absolute_final_round(player.round_number):
            player.participant.q1 = player.q1
            player.participant.q2 = player.q2


class Prolific(DisruptionPage):
    @staticmethod
    def is_displayed(player: Player):
        return is_absolute_final_round(player.round_number)


# main sequence of pages for this otree app
# entire sequence is traversed every round
page_sequence = [
    HydratePlayer,
    Welcome,
    Instructions1,
    Instructions2,
    Instructions3,
    Disruption,
    Decide,
    Results,
    FinalResults,
    FinalQuestions,
    Prolific,
]
