import json
import random
from decimal import ROUND_HALF_UP, Decimal
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

import numpy as np
from otree.api import Currency, Page
from otree.lookup import PageLookup, _get_session_lookups
from otree.models import Participant, Session
from rich import print

from . import util
from .models import (Constants, Player, game_of_round, is_disrupt_round,
                     is_end_of_game, round_of_game, rounds_for_game,
                     should_disrupt_next_round)
from .treatment import Treatment, UnitCosts

# Form validation:
FORM_FIELD_VALIDATORS: Dict[str, Callable] = {}


def register_form_validator(form_field: str, validator: Callable) -> None:
    assert isinstance(form_field, str), f"field_name is not str - got {form_field} ({type(form_field)})"
    assert isinstance(validator, Callable), f"validator is not Callable - got {validator} ({type(validator)})"
    FORM_FIELD_VALIDATORS[form_field] = validator


def validate_participantid(val: Any) -> None:
    """Validate values of form_field "participantid" provided to the client."""

    form_field = "participantid"
    expect_type = str
    got = val
    got_type = type(val)
    if not isinstance(val, expect_type):
        return {form_field: f"{form_field} is expected to be {expect_type} - got {got} (type: {got_type})"}


def validate_ou(val: Any) -> None:
    """Validate values for form_field "ou" (order quantity) provided by the client."""

    form_field = "ou"
    expect_type = np.number
    got = val
    got_type = type(val)
    if not isinstance(val, expect_type):
        return {form_field: f"{form_field} (order quantity) is expected to be {expect_type} - got {got} (type: {got_type})"}


# register_form_validator(form_field="participantid", validator=validate_participantid)
register_form_validator(form_field="ou", validator=validate_ou)


def print_form_values(player: Player, values: Any) -> None:
    """Print a page's form values to console."""
    if values:
        print(f"Page has form values: ", values)


def decorate_error_message(func) -> Callable:
    """Decorator designed to wrap a custom Page error_message handler to print page form values to console before running
    the handler.
    """

    @wraps(func)
    def wrapped_error_message_handler(player: Player, values: Any) -> Optional[Union[dict, str]]:
        """Example ``error_message`` from https://otree.readthedocs.io/en/latest/misc/tips_and_tricks.html#avoid-duplicated-validation-methods:


        >>> @staticmethod
            def error_message(player, values):
                error_messages = dict()

                for field_name in values:
                    if field_name in form_field_validators:
                        validator = form_field_validators[field_name]
                        try:
                            validator(values[key])
                        except Exception as e:
                            error_messages[field_name] = str(e)

                return error_messages
        """
        print_form_values(values)
        return func(player, values)

    return wrapped_error_message_handler


def default_vars_for_template(player: Player) -> dict:

    from otree import settings

    session: Session = player.session
    info: PageLookup = _get_session_lookups(session.code)[player.round_number]
    page_class: Type = info.page_class
    page_name = getattr(page_class, "__qualname__", getattr(page_class, "__name__", None))
    participant: Participant = player.participant
    round_number = player.round_number
    game_number = game_of_round(player.round_number)
    game_round = round_of_game(player.round_number)
    game_rounds = rounds_for_game(game_number)

    treatment: Treatment = player.participant.vars.get("treatment", None)

    unit_costs = player.participant.vars.get("unit_costs", None)
    rcpu = float(unit_costs.rcpu) if unit_costs else None
    wcpu = float(unit_costs.wcpu) if unit_costs else None
    hcpu = float(unit_costs.hcpu) if unit_costs else None

    _vars = dict(
        language_code=settings.LANGUAGE_CODE,
        real_world_currency_code=settings.REAL_WORLD_CURRENCY_CODE,
        games=Constants.num_games,
        rounds=Constants.rounds_per_game,
        page_name=page_name,
        round_number=round_number,
        game_number=game_number,
        game_round=game_round,
        session_code=session.code,
        participant_code=participant.code,
        is_end_of_game=is_end_of_game(player.round_number),
        is_disruption_next_round=should_disrupt_next_round(player),
        is_disruption_round=is_disrupt_round(player),
        is_done=player.round_number == Constants.num_rounds,
        starttime=player.participant.vars.get("starttime", None),
        variance_choice=treatment.variance_choice if treatment else None,
        disruption_choice=treatment.disruption_choice if treatment else None,
        rcpu=rcpu,
        wcpu=wcpu,
        hcpu=hcpu,
        optimal_order_quantity=max(0, round(treatment.get_optimal_order_quantity() - player.participant.vars.get("stock_units", 0))) if treatment else None,
        su_prior=player.participant.vars.get("stock_units"),
        su=player.field_maybe_none("su"),
        ou=player.field_maybe_none("ou"),
        du=player.field_maybe_none("du"),
        revenue=player.field_maybe_none("revenue"),
        cost=player.field_maybe_none("cost"),
        profit=player.field_maybe_none("profit"),
        history=player.participant.vars.get("history", None),
        game_results=player.participant.vars.get("game_results", None),
    )

    print(
        f"[yellow]{page_name} Page:  Round number: {player.round_number}, Game number: {game_number}, Game's last round: {game_rounds[-1]}, Round in game: {game_round}[/]"
    )

    return _vars


Page.error_message = staticmethod(print_form_values)
Page.vars_for_template = staticmethod(default_vars_for_template)


def frontend_format_currency(currency: Currency, as_integer: bool = False) -> str:
    import re

    symbol = re.sub(r"([^0-9.]+)(.*)", "\\1", str(currency))
    if as_integer:
        decimals = 0
    else:
        decimals = len(str(currency).split(".")[1])
    c_str = f"{symbol}{float(str(currency).replace(symbol,'')):,.{decimals}f}"
    return c_str


def init_game_history() -> List[Dict[str, Any]]:
    return [
        dict(
            period=i + 1,
            su_before=0 if i == 0 else None,
            su_after=None,
            ou=None,
            du=None,
            revenue=None,
            cost=None,
            profit=None,
            cumulative_profit=None,
        )
        for i in range(Constants.rounds_per_game)
    ]


class Welcome(Page):
    # form_model = "player"
    # form_fields = ["participantid"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        _vars = default_vars_for_template(player).copy()
        _vars.update(page_name="Welcome")
        return _vars

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:
        treatment = Treatment.choose()
        starttime = util.get_time()
        unit_costs = treatment.get_unit_costs()
        demand_rvs = treatment.get_demand_rvs(Constants.rvs_size)

        player.participant.treatment = treatment
        player.participant.starttime = starttime
        player.participant.stock_units = 0
        player.participant.unit_costs = unit_costs
        player.participant.demand_rvs = demand_rvs
        player.participant.game_results = []
        player.participant.history = init_game_history()

        player.starttime = starttime
        player.endtime = None
        player.rcpu = unit_costs.rcpu
        player.wcpu = unit_costs.wcpu
        player.hcpu = unit_costs.hcpu
        player.su = None
        player.ou = None
        player.du = None
        player.revenue = None
        player.cost = None
        player.profit = None


class Disruption(Page):
    @staticmethod
    def is_displayed(player: Player):
        return is_disrupt_round(player)

    @staticmethod
    def vars_for_template(player: Player):
        _vars = default_vars_for_template(player).copy()
        _vars.update(page_name="Disruption", allow_disruption=Constants.allow_disruption)
        return _vars

    @staticmethod
    def js_vars(player: Player):
        _vars = Disruption.vars_for_template(player).copy()
        return _vars

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if Constants.allow_disruption:
            player.participant.demand_rvs = player.participant.treatment.get_demand_rvs(Constants.rvs_size, disrupt=True)


class Decide(Page):

    form_model = "player"
    form_fields = ["ou"]

    @staticmethod
    def vars_for_template(player: Player):
        _vars = default_vars_for_template(player).copy()
        idx = round_of_game(player.round_number) - 1
        hist = player.participant.history[idx]
        if hist.get("su_before") is None:
            hist.update(su_before=player.participant.stock_units)
        player.participant.history[idx] = hist
        _vars.update(page_name="Decide", history=player.participant.history)
        return _vars

    @staticmethod
    def js_vars(player: Player) -> dict:
        _vars = Decide.vars_for_template(player).copy()
        _vars.update(demand_rvs=player.participant.vars.get("demand_rvs"))
        return _vars

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:

        game_number = game_of_round(player.round_number)
        game_rounds = rounds_for_game(game_number)

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
        cumulative_profit = sum(p.profit for p in player.in_rounds(game_rounds[0], player.round_number - 1)) + player.profit

        # history
        idx = round_of_game(player.round_number) - 1
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
            # formatted_cumulative_profit=frontend_format_currency(cumulative_profit, as_integer=True),
        )
        player.participant.history[idx] = hist
        print("%s" % player.participant.history)


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        _vars = Decide.vars_for_template(player).copy()
        _vars.update(page_name="Results")
        return _vars

    @staticmethod
    def js_vars(player: Player):
        _vars = Results.vars_for_template(player).copy()
        _vars.update(demand_rvs=player.participant.vars.get("demand_rvs"))
        return _vars

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:
        if is_end_of_game(player.round_number):
            ## NOTE: old "game_results" data
            ## game_number = game_of_round(player.round_number)
            ## rounds = rounds_for_game(game_number)
            ## game_rev, game_cost, game_profit = 0, 0, 0
            ## for p in player.in_rounds(rounds[0], rounds[-1]):
            ##     game_rev += p.revenue
            ##     game_cost += p.cost
            ##     game_profit += p.profit
            ## player.participant.game_results.append(dict(revenue=game_rev, cost=game_cost, profit=game_profit))

            # NOTE: new "game_results" = game history
            player.participant.game_results.append(player.participant.history)

            player.participant.history = init_game_history()
            player.participant.stock_units = 0

            player.endtime = util.get_time()


class FinalResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return is_end_of_game(player.round_number)

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        _vars = Decide.vars_for_template(player).copy()
        _vars.update(
            page_name="FinalResults",
            is_done=player.round_number == Constants.num_rounds,
            next_game=game_of_round(player.round_number) + 1,
            game_results=player.participant.vars.get("game_results", None),
        )
        return _vars

    @staticmethod
    def js_vars(player: Player) -> dict:
        _vars = FinalResults.vars_for_template(player).copy()
        _vars.update(demand_rvs=player.participant.vars.get("demand_rvs"))
        return _vars

    # @staticmethod
    # def before_next_page(player: Player, **kwargs) -> None:
    #     if is_end_of_game(player.round_number):
    #         player.participant.stock_units = 0
    #         game_number = game_of_round(player.round_number)
    #         rounds = rounds_for_game(game_number)
    #         game_rev, game_cost, game_profit = 0, 0, 0
    #         for p in player.in_rounds(rounds[0], rounds[-1]):
    #             game_rev += p.revenue
    #             game_cost += p.cost
    #             game_profit += p.profit
    #         player.participant.game_results.append(dict(revenue=game_rev, cost=game_cost, profit=game_profit))
    #         player.participant.history = init_game_history()

    #         player.endtime = util.get_time()


# main sequence of pages for this otree app
# entire sequence is traversed every round
page_sequence = [Welcome, Disruption, Decide, Results, FinalResults]
