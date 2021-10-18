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
from .models import (
    ALLOW_DISRUPTION,
    GAMES,
    ROUNDS,
    RVS_SIZE,
    Constants,
    Player,
    game_of_round,
    is_end_of_game,
    round_of_game,
    rounds_for_game,
    should_disrupt_next_round,
)
from .treatment import Treatment, UnitCosts

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
    page_name = getattr(page_class, "__qualname__", "__name__")
    participant: Participant = player.participant
    round_number = player.round_number
    game_number = game_of_round(player.round_number)
    game_round = round_of_game(player.round_number)
    game_rounds = rounds_for_game(game_number)

    treatment: Treatment = player.participant.vars.get("treatment", None)

    _vars = dict(
        language_code=settings.LANGUAGE_CODE,
        real_world_currency_code=settings.REAL_WORLD_CURRENCY_CODE,
        games=GAMES,
        rounds=ROUNDS,
        page_name=page_name,
        round_number=round_number,
        game_number=game_number,
        game_round=game_round,
        session_code=session.code,
        participant_code=participant.code,
        is_end_of_game=is_end_of_game(player.round_number),
        is_disruption_next_round=should_disrupt_next_round(player),
        is_done=player.round_number == Constants.num_rounds,
        starttime=player.participant.vars.get("starttime", None),
        history=player.participant.vars.get("history", None),
        variance=treatment.variance_choice if treatment else None,
        # session_vars=str(session.vars),
        # participant_vars=str({k: v for k, v in participant.vars.items() if k != "demand_rvs"}),
        # participant_session_id=participant.session_id,
        # participant_id=participant.id,
        # participant_id_in_session=participant.id_in_session,
        # player_id=player.id,
        # player_id_in_subsession=player.id_in_subsession,  # equals ``participant.id_in_session``
    )

    print(
        f"[yellow]{page_name} Page:  Round number: {player.round_number}, Game number: {game_number}, Game's last round: {game_rounds[-1]}, Round in game: {game_round}[/]"
    )

    return _vars


def default_js_vars(player: Player) -> dict:
    _vars = default_vars_for_template(player).copy()

    _vars.update(demand_rvs=player.participant.vars.get("demand_rvs"))
    return _vars


Page.vars_for_template = staticmethod(default_vars_for_template)
Page.error_message = staticmethod(print_form_values)
Page.js_vars = staticmethod(default_js_vars)


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
            su=0 if i == 0 else None,
            ou=None,
            du=None,
            profit=None,
            cumulative_profit=None,
            # formatted_cumulative_profit=None,
        )
        for i in range(ROUNDS)
    ]


class Welcome(Page):
    # form_model = "player"
    # form_fields = ["participantid"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:
        treatment = Treatment.choose()
        starttime = util.get_time()
        unit_costs = treatment.get_unit_costs()
        demand_rvs = treatment.get_demand_rvs(RVS_SIZE)

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
        player.su = 0
        player.ou = None
        player.du = None
        player.revenue = None
        player.cost = None
        player.profit = None


class Decide(Page):

    form_model = "player"
    form_fields = ["ou"]

    @staticmethod
    def vars_for_template(player: Player):

        game_number = game_of_round(player.round_number)
        game_rounds = rounds_for_game(game_number)
        unit_costs = player.participant.unit_costs
        su_prior = player.participant.stock_units

        d = dict(
            rcpu=unit_costs.rcpu,
            wcpu=unit_costs.wcpu,
            hcpu=unit_costs.hcpu,
            su_prior=su_prior,
            su=player.field_maybe_none("su"),
            ou=player.field_maybe_none("ou"),
            du=player.field_maybe_none("du"),
            revenue=player.field_maybe_none("revenue"),
            cost=player.field_maybe_none("cost"),
            profit=player.field_maybe_none("profit"),
            total_profit=Currency(sum(p.profit for p in player.in_rounds(game_rounds[0], player.round_number - 1))),
        )
        _vars = default_vars_for_template(player).copy()
        _vars.update(d)
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

        # rcpu, wcpu, hcpu = [25.00, 14.00, 6.00]

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
        hist.update(
            ou=player.ou,
            du=player.du,
            su=player.su,
            profit=float(player.profit),
            cumulative_profit=cumulative_profit,
            # formatted_cumulative_profit=frontend_format_currency(cumulative_profit, as_integer=True),
        )
        player.participant.history[idx] = hist
        print("%s" % player.participant.history)

        # player.participant.history[game_of_round(player.round_number) - 1][player.round_number - 1] = dict(ou=ou, du=du, su=su)
        # print(
        #     f"game_of_round(player.round_number) - 1: {game_of_round(player.round_number) - 1}, len(player.participant.history): {len(player.participant.history)}, len(player.participant.history\[game_of_round(player.round_number) - 1\]): {len(player.participant.history[game_of_round(player.round_number) - 1])}, player.participant.history\[game_of_round(player.round_number) - 1\]: {player.participant.history[game_of_round(player.round_number) - 1]}"
        # )

        # for dct in player.participant.history:
        #     if dct.get("group") == "ou":
        #         dct[round_of_game(player.round_number)] = player.ou
        #     elif dct.get("group") == "du":
        #         dct[round_of_game(player.round_number)] = player.du
        #     elif dct.get("group") == "su":
        #         dct[round_of_game(player.round_number)] = player.su


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):

        _vars = default_vars_for_template(player).copy()
        d = dict(
            revenue=player.revenue,
            cost=player.cost,
            du=int(round(player.du)),
            ou=int(round(player.ou)),
            su=int(round(player.participant.stock_units)),
            profit=float(player.profit),
            # formatted_profit=frontend_format_currency(player.profit, as_integer=True),
        )
        _vars.update(d)
        return _vars

    @staticmethod
    def js_vars(player: Player):

        _vars = default_js_vars(player).copy()
        d = dict(
            revenue=player.revenue,
            cost=player.cost,
            du=int(round(player.du)),
            ou=int(round(player.ou)),
            su=int(round(player.participant.stock_units)),
            profit=float(player.profit),
            # formatted_profit=frontend_format_currency(player.profit, as_integer=True),
        )
        _vars.update(d)
        return _vars

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:
        if is_end_of_game(player.round_number):
            # results = player.participant.round_results
            player.participant.stock_units = 0
            game_number = game_of_round(player.round_number)
            rounds = rounds_for_game(game_number)
            game_rev, game_cost, game_profit = 0, 0, 0
            for p in player.in_rounds(rounds[0], rounds[-1]):
                game_rev += p.revenue
                game_cost += p.cost
                game_profit += p.profit
            player.participant.game_results.append(dict(revenue=game_rev, cost=game_cost, profit=game_profit))
            player.participant.history = init_game_history()

        player.endtime = util.get_time()


class Disruption(Page):
    @staticmethod
    def is_displayed(player: Player):
        return should_disrupt_next_round(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(ALLOW_DISRUPTION=ALLOW_DISRUPTION)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if ALLOW_DISRUPTION:
            player.participant.demand_rvs = player.participant.treatment.get_demand_rvs(RVS_SIZE, disrupt=True)


class FinalResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return is_end_of_game(player.round_number)

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        _vars = default_vars_for_template(player).copy()
        _vars.update(
            is_done=player.round_number == Constants.num_rounds,
            next_game=game_of_round(player.round_number) + 1,
            game_results=player.participant.game_results,
        )
        return _vars

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:
        player.endtime = util.get_time()


# main sequence of pages for this otree app
# entire sequence is traversed every round
page_sequence = [Welcome, Decide, Results, FinalResults]
