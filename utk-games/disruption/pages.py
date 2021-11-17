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

from .constants import DISRUPTION_ROUND_IN_GAMES
from .formvalidation import (default_error_message,
                             register_form_field_validator)
from .models import Constants, Player, initialize_game_history
from .treatment import Treatment, UnitCosts
from .util import (as_static_path, get_app_name, get_game_number,
                   get_game_rounds, get_optimal_order_quantity, get_page_name,
                   get_round_in_game, get_time, is_absolute_final_round,
                   is_disruption_next_round, is_disruption_this_round,
                   is_game_over)

Page.error_message = staticmethod(default_error_message)


@register_form_field_validator(form_field="is_planner", expect_type=bool)
def validate_is_planner(is_planner: bool) -> Optional[str]:
    if is_planner is False:
        return f"""Must be True to proceed."""
    return


@register_form_field_validator(form_field="years_as_planner", expect_type=int)
def validate_years_as_planner(years_as_planner: int) -> Optional[str]:
    if years_as_planner < 0:
        return f"""Number must be >= 0."""
    return


@register_form_field_validator(form_field="company_name", expect_type=str)
def validate_company_name(company_name: str) -> Optional[str]:
    import re

    if not re.findall(r"[a-zA-Z]", str(company_name)):
        return f"""Enter a name."""
    return


@register_form_field_validator(form_field="does_consent", expect_type=bool)
def validate_does_consent(does_consent: bool) -> Optional[str]:
    if does_consent is False:
        return f"""Must consent to proceed."""
    return


def vars_for_template(player: Player) -> dict:

    from otree.settings import (LANGUAGE_CODE, LANGUAGE_CODE_ISO,
                                REAL_WORLD_CURRENCY_CODE,
                                REAL_WORLD_CURRENCY_DECIMAL_PLACES)

    treatment: Treatment = player.participant.vars.get("treatment", None)

    distribution_png, disrupted_distribution_png = treatment.save_distribution_plots()

    _vars = dict(
        language_code=LANGUAGE_CODE,
        real_world_currency_code=REAL_WORLD_CURRENCY_CODE,
        real_world_currency_decimal_places=REAL_WORLD_CURRENCY_DECIMAL_PLACES,
        games=Constants.num_games,
        rounds=Constants.rounds_per_game,
        allow_disruption=Constants.allow_disruption,
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
        disruption_round=DISRUPTION_ROUND_IN_GAMES.get(player.game_number, None)
        if treatment.disruption_choice and player.game_number == 1
        else None,
        distribution_png=as_static_path(distribution_png),
        disrupted_distribution_png=as_static_path(distribution_png if player.game_number == 1 and not treatment.disruption_choice else disrupted_distribution_png),
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
        payoff_round=player.participant.vars.get("payoff_round", None),
        payoff=player.participant.vars.get("payoff", None),
        treatment=treatment.idx,
    )

    # make Currency (Decimal) objects json serializable
    for ckey in ["rcpu", "wcpu", "hcpu", "revenue", "cost", "profit"]:
        val = _vars.get(ckey)
        _vars.update({ckey: float(val) if val else None})

    return _vars


def js_vars(player: Player) -> dict:
    _vars = Page.vars_for_template(player).copy()
    treatment = player.participant.treatment
    _vars.update(demand_rvs=treatment.get_demand_rvs())
    return _vars


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
        player.treatment = player.participant.treatment.idx
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
        player.payoff_round = player.participant.payoff_round

        extras = dict(su=player.su, ooq=player.ooq, is_planner=player.field_maybe_none("is_planner"))
        print(
            f"hydrate_player: Round {player.round_number}: {get_page_name(player)} Page, Game {player.game_number} (ends on round {get_game_rounds(player.round_number)[-1]}), Period number: {player.period_number}, player extras: {extras}"
        )


class Welcome(Page):
    form_model = "player"
    form_fields = ["is_planner", "years_as_planner", "company_name", "does_consent"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

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
            player.participant.treatment.get_demand_rvs(Constants.rvs_size, disrupt=True)


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
        du = round(random.choice(player.participant.treatment._demand_rvs))
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

        if player.round_number == player.participant.payoff_round:
            player.payoff = Currency(min(1750, max(750, player.profit * 0.05)))
            player.participant.payoff = player.payoff
        else:
            player.payoff = Currency(0)


class Results(Page):
    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:
        player.endtime = get_time()
        if is_game_over(player.round_number):
            # store game history & flush game state
            player.participant.game_results.append(player.participant.history)
            player.participant.history = initialize_game_history()
            player.participant.stock_units = 0
            player.participant.treatment.reset()


class FinalResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return is_game_over(player.round_number)


# main sequence of pages for this otree app
# entire sequence is traversed every round
page_sequence = [HydratePlayer, Welcome, Disruption, Decide, Results, FinalResults]
