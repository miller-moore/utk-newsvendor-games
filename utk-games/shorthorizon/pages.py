import random
from decimal import ROUND_HALF_UP, Decimal
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union
from uuid import uuid4

import numpy as np
from otree.api import Currency, Page
from otree.lookup import PageLookup, _get_session_lookups
from otree.models import Participant
from rich import print

from .constants import Constants
from .formvalidation import error_message_decorator
from .models import Player, initialize_game_history
from .treatment import Treatment, UnitCosts
from .util import (
    get_game_number,
    get_game_rounds,
    get_optimal_order_quantity,
    get_page_name,
    get_round_in_game,
    get_time,
    is_absolute_final_round,
    is_disruption_next_round,
    is_disruption_this_round,
    is_game_over,
)


@error_message_decorator
def error_message(player: Player, formfields: Any):
    from .formvalidation import FORM_FIELD_VALIDATORS

    if not type(formfields) is dict:
        return

    error_messages = dict()
    for field in formfields:
        if field in FORM_FIELD_VALIDATORS:
            validate = FORM_FIELD_VALIDATORS[field]
            values = formfields[field]
            try:
                validate(values)
            except Exception as e:
                error_messages[field] = str(e)
    return error_messages


def vars_for_template(player: Player) -> dict:

    from otree.settings import LANGUAGE_CODE, LANGUAGE_CODE_ISO, REAL_WORLD_CURRENCY_CODE, REAL_WORLD_CURRENCY_DECIMAL_PLACES

    treatment: Treatment = player.participant.vars.get("treatment", None)

    _vars = dict(
        language_code=LANGUAGE_CODE,
        real_world_currency_code=REAL_WORLD_CURRENCY_CODE,
        real_world_currency_decimal_places=REAL_WORLD_CURRENCY_DECIMAL_PLACES,
        games=Constants.num_games,
        rounds=Constants.rounds_per_game,
        allow_disruption=Constants.allow_disruption,
        page_name=get_page_name(player),
        round_number=player.round_number,
        game_number=player.game_number,  # game_number,
        game_round=player.period_number,  # game_round,
        period_number=player.period_number,  # game_round,
        session_code=player.session.code,
        participant_code=player.participant.code,
        variance_choice=treatment.variance_choice if treatment else None,
        disruption_choice=treatment.disruption_choice if treatment else None,
        is_disruption_this_round=is_disruption_this_round(player),
        is_disruption_next_round=is_disruption_next_round(player),
        is_game_over=is_game_over(player.round_number),
        is_absolute_final_round=is_absolute_final_round(player.round_number),
        uuid=player.field_maybe_none("uuid"),
        starttime=player.field_maybe_none("starttime"),
        endtime=player.field_maybe_none("endtime"),
        is_planner=player.field_maybe_none("is_planner"),
        years_as_planner=player.field_maybe_none("years_as_planner"),
        company_name=player.field_maybe_none("company_name"),
        does_consent=player.field_maybe_none("does_consent"),
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
    )

    # make Currency (Decimal) objects json serializable
    for ckey in ["rcpu", "wcpu", "hcpu", "revenue", "cost", "profit"]:
        val = _vars.get(ckey)
        _vars.update({ckey: float(val) if val else None})

    return _vars


def js_vars(player: Player) -> dict:
    _vars = Page.vars_for_template(player).copy()
    _vars.update(demand_rvs=player.participant.vars.get("demand_rvs", None))
    return _vars


Page.error_message = staticmethod(error_message)
Page.vars_for_template = staticmethod(vars_for_template)
Page.js_vars = staticmethod(js_vars)


class HydratePlayer(Page):

    timeout_seconds = 0

    @staticmethod
    def before_next_page(player: Player, **kwargs):
        """Hydrates player from participant. The participant is hydrated in `creating_subsession` (in models.py)."""
        player.uuid = player.participant.uuid
        player.starttime = get_time()
        player.endtime = None
        player.treatment = player.participant.treatment.json()
        player.is_planner = player.participant.is_planner
        player.years_as_planner = player.participant.years_as_planner
        player.company_name = player.participant.company_name
        player.does_consent = player.participant.does_consent
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

        extras = dict(su=player.su, ooq=player.ooq, is_planner=player.field_maybe_none("is_planner"))
        print(
            f"[green]hydrate_player: Round {player.round_number}: {get_page_name(player)} Page, Game {player.game_number} (ends on round {get_game_rounds(player.round_number)[-1]}), Period number: {player.period_number}, player extras: {extras}"
        )


class Welcome(Page):
    form_model = "player"
    form_fields = ["is_planner", "years_as_planner", "company_name", "does_consent"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    # @staticmethod
    # def get_form_fields(player: Player) -> List[str]:
    #     """Generate formfields dynamically for the Page template whether or not defined as a field in the Player model.
    #     if player.f3:
    #         return ["f1", "f2", "f3"]
    #     else:
    #         return ["f1", "f2"]
    #     """
    #     return Welcome.form_fields

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.is_planner = player.is_planner
        player.participant.years_as_planner = player.years_as_planner
        player.participant.company_name = player.company_name
        player.participant.does_consent = player.does_consent


class Disruption(Page):
    @staticmethod
    def is_displayed(player: Player):
        return is_disruption_this_round(player)

    @staticmethod
    def before_next_page(player: Player, **kwargs):
        if Constants.allow_disruption:
            player.participant.demand_rvs = player.participant.treatment.get_demand_rvs(Constants.rvs_size, disrupt=True)
            # TODO: update participant's mu & sigma to transformed values even tho demand_rvs is the thing that matters in practice
            # player.participant.treatment.get_distribution_parameters()


class Decide(Page):

    form_model = "player"
    form_fields = ["ou"]

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:

        # unit costs
        unit_costs = player.participant.unit_costs
        rcpu = float(unit_costs.rcpu)
        wcpu = float(unit_costs.wcpu)
        hcpu = float(unit_costs.hcpu)

        # unit quantities
        su = round(player.participant.stock_units)
        du = round(random.choice(player.participant.demand_rvs))
        ou = round(player.ou)

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


class Results(Page):
    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:
        player.endtime = get_time()
        if is_game_over(player.round_number):
            # store game history & flush game state
            player.participant.game_results.append(player.participant.history)
            player.participant.history = initialize_game_history()
            player.participant.stock_units = 0


class FinalResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return is_game_over(player.round_number)


class NextApp(Page):
    timeout_seconds = 0

    # @staticmethod
    # def is_displayed(player: Player):
    #     print(
    #         f"""[orange]is_displayed: Round: {player.round_number}: {get_page_name(player)} Page, is_absolute_final_round? {is_absolute_final_round(player.round_number)}[/]"""
    #     )
    #     return is_absolute_final_round(player.round_number)

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps: List[str]) -> Optional[str]:
        """See https://otree.readthedocs.io/en/self/pages.html?highlight=app_after_this_page#app-after-this-page

        Implemented to determine which app to skip to next based on conditions of this app ('shorthorizon')
        and any other arbitrary logic as desired.

        Parameters
        ----------
        player : Player
        upcoming_apps : [list[str]]
            List of upcoming app names or an empty list.

        Returns
        ----------
        [Optional[str]]
            The name of the next app in app_sequence (or None).
        """

        def printer(next_app):
            print(
                f"""[purple]app_after_this_page: Round: {player.round_number!r}: {get_page_name(player)!r} Page, is_absolute_final_round? {is_absolute_final_round(player.round_number)!r}, upcoming_apps: {upcoming_apps!r}, next app: {next_app!r}"""
            )

        next_app = None
        if upcoming_apps:
            if upcoming_apps[0] == "disruption":
                # skip over 'disruption' app
                upcoming_apps.pop()
                try:
                    next_app = upcoming_apps.pop()
                except:
                    pass
            else:
                next_app = upcoming_apps[0]
        printer(next_app)
        return next_app


# main sequence of pages for this otree app
# entire sequence is traversed every round
page_sequence = [HydratePlayer, Welcome, Disruption, Decide, Results, FinalResults, NextApp]
