import random
from decimal import ROUND_HALF_UP, Decimal
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union
from uuid import uuid4

import numpy as np
from otree.api import Currency
from otree.api import Page as OTreePage
from otree.lookup import PageLookup, _get_session_lookups
from rich import print

from .formvalidation import error_message_decorator
from .models import Constants, Player
from .treatment import Treatment, UnitCosts
from .util import (
    get_game_number,
    get_game_rounds,
    get_round_in_game,
    get_time,
    initialize_game_history,
    is_absolute_final_round,
    is_disruption_next_round,
    is_disruption_this_round,
    is_game_over,
    page_name,
)


class Page(OTreePage):
    @staticmethod
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

    @staticmethod
    def vars_for_template(player: Player) -> dict:

        Page.before_next_page(player)

        from otree.settings import (
            LANGUAGE_CODE,
            LANGUAGE_CODE_ISO,
            REAL_WORLD_CURRENCY_CODE,
            REAL_WORLD_CURRENCY_DECIMAL_PLACES,
        )

        game_number = get_game_number(player.round_number)
        game_rounds = get_game_rounds(player.round_number)
        game_round = get_round_in_game(player.round_number)

        treatment: Treatment = player.participant.vars.get("treatment", None)

        _vars = dict(
            language_code=LANGUAGE_CODE,
            real_world_currency_code=REAL_WORLD_CURRENCY_CODE,
            real_world_currency_decimal_places=REAL_WORLD_CURRENCY_DECIMAL_PLACES,
            games=Constants.num_games,
            rounds=Constants.rounds_per_game,
            allow_disruption=Constants.allow_disruption,
            page_name=page_name(player),
            round_number=player.round_number,
            game_number=game_number,
            game_round=game_round,
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

    @staticmethod
    def js_vars(player: Player) -> dict:
        _vars = Page.vars_for_template(player).copy()
        _vars.update(demand_rvs=player.participant.vars.get("demand_rvs", None))
        return _vars


class Welcome(Page):
    form_model = "player"
    form_fields = ["is_planner", "years_as_planner", "company_name", "does_consent"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def get_form_fields(player: Player) -> List[str]:
        """Generate formfields dynamically for the Page template whether or not defined as a field in the Player model.
        if player.f3:
            return ["f1", "f2", "f3"]
        else:
            return ["f1", "f2"]
        """
        return Welcome.form_fields

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:
        game_number = get_game_number(player.round_number)
        round_in_game = get_round_in_game(player.round_number)
        game_rounds = get_game_rounds(player.round_number)
        print(
            f"[green]{page_name(player)} Page:  Round number: {player.round_number}, Game number: {game_number}, Game's last round: {game_rounds[-1]}, Round in game: {round_in_game}[/]"
        )
        player.is_planner = player.participant.is_planner
        player.years_as_planner = player.participant.years_as_planner
        player.company_name = player.participant.company_name
        player.does_consent = player.participant.does_consent


class Disruption(Page):
    @staticmethod
    def is_displayed(player: Player):
        return is_disruption_this_round(player)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if Constants.allow_disruption:
            player.participant.demand_rvs = player.participant.treatment.get_demand_rvs(Constants.rvs_size, disrupt=True)


class Decide(Page):

    form_model = "player"
    form_fields = ["ou"]

    @staticmethod
    def vars_for_template(player: Player):
        _vars = Page.vars_for_template(player).copy()
        idx = get_round_in_game(player.round_number) - 1
        hist = player.participant.history[idx]
        if hist.get("su_before") is None:
            hist.update(su_before=player.participant.stock_units)
        player.participant.history[idx] = hist
        _vars.update(history=player.participant.history)
        return _vars

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:

        player.is_planner = player.participant.is_planner
        player.years_as_planner = player.participant.years_as_planner
        player.company_name = player.participant.company_name
        player.does_consent = player.participant.does_consent

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
        first_round_in_game = get_game_rounds(player.round_number)
        cumulative_profit = (
            sum(p.profit for p in player.in_rounds(first_round_in_game[0], player.round_number - 1)) + player.profit
        )

        # history
        idx = get_round_in_game(player.round_number) - 1
        hist = player.participant.history[idx]
        if hist.get("su_before") is None:
            hist.update(su_before=su)
        hist.update(
            ou=ou,
            du=du,
            su_after=su_new,
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

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        _vars = Decide.vars_for_template(player).copy()
        _vars.update(
            game_results=player.participant.game_results,
        )
        return _vars

    @staticmethod
    def js_vars(player: Player) -> dict:
        _vars = FinalResults.vars_for_template(player).copy()
        return _vars


# main sequence of pages for this otree app
# entire sequence is traversed every round
page_sequence = [Welcome, Disruption, Decide, Results, FinalResults]
