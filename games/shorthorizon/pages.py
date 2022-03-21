import os
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

from .constants import PRACTICE_ROUNDS, C
from .formvalidation import default_error_message, register_form_field_validator
from .models import Player
from .treatment import Distribution, Treatment
from .util import (
    as_static_path,
    call_safe,
    get_app_name,
    get_game_number,
    get_game_rounds,
    get_optimal_order_quantity,
    get_page_name,
    get_real_round_number,
    get_room_display_name,
    get_room_name,
    get_round_in_game,
    get_time,
    initialize_game_history,
    is_absolute_final_round,
    is_game_over_round,
    is_practice_over_round,
    is_practice_round,
)

from common.colors import COLORS  # isort:skip
from common.google_image_downloader import GoogleImageDownloader  # isort:skip


# # fetch images of Smokey the dog to display in an otherwise blank canvas region in the browser page
SMOKEY_IMAGES_DIR = (C.STATIC_DIR / ".." / "smokey_images").resolve()
SMOKEY_IMAGES_DIR.mkdir(exist_ok=True)
# if len(list(SMOKEY_IMAGES_DIR.glob("*.jpg"))) < 5:

#     smokey_the_dog_image_fetcher = GoogleImageDownloader(
#         query="utk-smokey-the-dog", api_key=os.getenv("SERPAPI_KEY", None), download_directory=SMOKEY_IMAGES_DIR, max_count=10
#     )
#     smokey_the_dog_image_fetcher.start()


@register_form_field_validator(form_field="is_planner", expect_type=bool)
def validate_is_planner(is_planner: bool) -> Optional[str]:
    # This field really indicates whether the participant (or student) carries the desired role/field-of-study for the experiment.
    # But allow anyone to participate because why not (ie., do nothing).
    return


@register_form_field_validator(form_field="gender_identity", expect_type=str)
def validate_does_consent(gender_identity: str) -> Optional[str]:
    # totally optional field provided at the user's will
    # hence, any value is valid (ie., do nothing)
    return


@register_form_field_validator(form_field="does_consent", expect_type=bool)
def validate_does_consent(does_consent: bool) -> Optional[str]:
    if does_consent is False:
        return f"""Must consent."""
    return


class ShortHorizonPage(Page):

    error_message = staticmethod(default_error_message)

    @staticmethod
    def vars_for_template(player: Player) -> dict:

        from otree.settings import (
            LANGUAGE_CODE,
            LANGUAGE_CODE_ISO,
            REAL_WORLD_CURRENCY_CODE,
            REAL_WORLD_CURRENCY_DECIMAL_PLACES,
        )

        # import importlib
        # from . import treatment as shorthorizon_treatment
        # treatment_module = importlib.reload(shorthorizon_treatment)

        treatment: Treatment = player.participant.treatment
        is_practice = is_practice_round(player.round_number)
        distribution: Distribution
        if is_practice:
            distribution = treatment.get_practice_distribution()
        else:
            distribution = treatment.get_distribution()

        payoff_round = player.participant.vars.get("payoff_round", None)

        _vars = dict(
            language_code=LANGUAGE_CODE,
            real_world_currency_code=REAL_WORLD_CURRENCY_CODE,
            real_world_currency_decimal_places=REAL_WORLD_CURRENCY_DECIMAL_PLACES,
            smokey_img_file=str(
                Path().joinpath(SMOKEY_IMAGES_DIR.name, random.choice(list(SMOKEY_IMAGES_DIR.glob("*.jpg"))).name)
            ),
            colors=COLORS.copy(),
            games=C.NUM_GAMES,
            rounds=C.ROUNDS_PER_GAME,
            room_name=get_room_name(player),
            room_display_name=get_room_display_name(player),
            page_name=get_page_name(player),
            app_name=get_app_name(player),
            round_number=player.round_number,
            real_round_number=get_real_round_number(player.round_number),
            game_number=player.game_number,  # game_number,
            game_rounds=get_game_rounds(get_real_round_number(player.round_number)),
            period_number=player.period_number,  # starts at 1 and updated via get_round_in_game in page HydratePlayer (below)
            session_code=player.session.code,
            participant_code=player.participant.code,
            variance_choice=None,
            disruption_choice=None,
            disruption_round=None,
            distribution_png=as_static_path(treatment.get_distribution_png(is_practice)),  # Decide.html
            consent_form_pdf=as_static_path(treatment.get_consent_form_pdf()),  # Consent.html
            instructions_pdf=as_static_path(treatment.get_instructions_pdf()),  # various
            snapshot_instructions_1_png=as_static_path(treatment.get_snapshot_instruction_png(n=1)),  # Instructions3.html
            snapshot_instructions_2_png=as_static_path(treatment.get_snapshot_instruction_png(n=2)),  # Instructions3.html
            snapshot_instructions_3_png=as_static_path(treatment.get_snapshot_instruction_png(n=3)),  # Instructions3.html
            is_practice_round=is_practice_round(player.round_number),
            is_practice_over_round=is_practice_over_round(player.round_number),
            is_pilot_test=player.session.config.get("is_pilot_test", False),
            is_disrupted=treatment.is_disrupted(),
            is_disruption_this_round=False,
            is_disruption_next_round=False,
            is_game_over_round=is_game_over_round(player.round_number),
            is_absolute_final_round=is_absolute_final_round(player.round_number),
            uuid=player.field_maybe_none("uuid"),
            starttime=player.field_maybe_none("starttime"),
            endtime=player.field_maybe_none("endtime"),
            is_planner=player.field_maybe_none("is_planner"),  # NOTE: demographic feature
            gender_identity=player.field_maybe_none("gender_identity"),  # NOTE: demographic feature
            does_consent=player.field_maybe_none("does_consent"),  # NOTE: demographic feature
            su=player.field_maybe_none("su"),
            ou=player.field_maybe_none("ou"),
            du=player.field_maybe_none("du"),
            ooq=player.field_maybe_none("ooq"),
            rcpu=player.field_maybe_none("rcpu"),
            wcpu=player.field_maybe_none("wcpu"),
            scpu=player.field_maybe_none("scpu"),
            revenue=player.field_maybe_none("revenue"),
            cost=player.field_maybe_none("cost"),
            profit=player.field_maybe_none("profit"),
            history=player.participant.vars.get("history", None),
            game_results=player.participant.vars.get("game_results", None),
            practice_results=player.participant.vars.get("practice_results", None),
            payoff_divisor=treatment.get_divisor(),
            payoff_round=payoff_round,
            payoff_round_profit=player.in_round(payoff_round).profit if payoff_round else Currency(0.0),
            payoff=player.participant.vars.get("payoff", None),
            treatment_id=treatment.id,
            practice_treatment_id=treatment.practice_treatment_id,
            profitex=treatment.get_profitex(),
            multiplier=treatment.get_multiplier(),
            profitex_multiplied=treatment.get_profitex() * treatment.get_multiplier(),
            mu=distribution.mu,
            sigma=distribution.sigma,
        )

        # make objects of type Decimal json serializable
        for ckey in _vars:
            if isinstance(_vars[ckey], Decimal):
                _vars[ckey] = float(_vars[ckey])

        return _vars

    @staticmethod
    def js_vars(player: Player) -> dict:
        _vars = ShortHorizonPage.vars_for_template(player).copy()
        treatment = player.participant.treatment
        _vars.update(demand_rvs=treatment.get_demand_rvs())
        return _vars


class HydratePlayer(ShortHorizonPage):

    timeout_seconds = 0

    @staticmethod
    def before_next_page(player: Player, **kwargs):
        """Hydrates player from participant. The participant is hydrated in `creating_subsession` (in models.py)."""
        print(f"Round {player.round_number}: {get_page_name(player)} Page")

        player.uuid = player.participant.uuid
        player.starttime = get_time()
        player.endtime = None
        player.treatment_id = player.participant.treatment.id
        player.practice_treatment_id = player.participant.treatment.practice_treatment_id
        player.is_planner = player.participant.is_planner  # Consent.html
        player.gender_identity = player.participant.gender_identity  # Consent.html
        player.does_consent = player.participant.does_consent  # Consent.html
        player.game_number = (
            0 if is_practice_round(player.round_number) else get_game_number(get_real_round_number(player.round_number))
        )
        player.period_number = get_real_round_number(player.round_number)
        player.su = None
        player.ou = None
        player.du = None
        player.ooq = get_optimal_order_quantity(player)

        treatment: Treatment = player.participant.treatment
        unit_costs = (
            treatment.get_practice_unit_costs() if is_practice_round(player.round_number) else treatment.get_unit_costs()
        )
        player.rcpu = unit_costs.rcpu
        player.wcpu = unit_costs.wcpu
        player.scpu = unit_costs.scpu
        player.revenue = 0
        player.cost = 0
        player.profit = 0
        player.payoff_round = player.participant.payoff_round


class Consent(ShortHorizonPage):
    form_model = "player"
    form_fields = ["is_planner", "gender_identity", "does_consent"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.is_planner = player.is_planner
        player.participant.gender_identity = player.gender_identity
        player.participant.does_consent = player.does_consent


class Instructions1(ShortHorizonPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Instructions2(ShortHorizonPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Instructions3(ShortHorizonPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class PracticeDecide(ShortHorizonPage):

    form_model = "player"
    form_fields = ["ou"]

    @staticmethod
    def is_displayed(player: Player):
        return is_practice_round(player.round_number)

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:

        treatment: Treatment = player.participant.treatment

        # unit costs
        # unit_costs = player.participant.unit_costs
        unit_costs = treatment.get_practice_unit_costs()
        rcpu = float(unit_costs.rcpu)
        wcpu = float(unit_costs.wcpu)
        scpu = float(unit_costs.scpu)

        # Get demand units!
        # NOTE: not randomly means from pre-determined data
        du = treatment.get_demand(randomly=False, player=player)
        # order units
        ou = player.ou
        # stock units
        su = max(0, ou - du)

        # revenue = rcpu * min(du, ou) + scpu * su
        # cost = wcpu * ou
        # profit = revenue - cost
        revenue = rcpu * min(du, ou) + scpu * su
        cost = wcpu * ou
        profit = revenue - cost

        # update player su, du, revenue, cost, profit, & payoff
        player.su = su
        player.du = du
        player.revenue = Currency(revenue)
        player.cost = Currency(cost)
        player.profit = Currency(profit)
        player.payoff = treatment.get_payoff(player)

        # update participant's history store corresponding to the current round in the current game
        idx = player.round_number - 1
        hist = player.participant.history[idx]

        hist.update(
            ou=ou,
            du=du,
            su=su,
            ooq=player.ooq,
            revenue=float(revenue),
            cost=float(cost),
            profit=float(profit),
            cumulative_profit=float(sum(p.profit for p in player.in_rounds(1, player.round_number))),
        )
        player.participant.history[idx] = hist


class PracticeResults(ShortHorizonPage):
    @staticmethod
    def is_displayed(player: Player):
        return is_practice_round(player.round_number)

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:
        player.endtime = get_time()
        if is_practice_over_round(player.round_number):
            # store game history & flush game state
            # player.participant.game_results.append(player.participant.history)
            player.participant.practice_results.append(player.participant.history)
            player.participant.history = initialize_game_history()


class PracticeResultsFinal(ShortHorizonPage):
    @staticmethod
    def is_displayed(player: Player):
        return is_practice_over_round(player.round_number)


class Decide(ShortHorizonPage):

    form_model = "player"
    form_fields = ["ou"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number > C.PRACTICE_ROUNDS

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:

        # unit costs
        # unit_costs = player.participant.unit_costs
        unit_costs = player.participant.treatment.get_unit_costs()
        rcpu = float(unit_costs.rcpu)
        wcpu = float(unit_costs.wcpu)
        scpu = float(unit_costs.scpu)

        # Get demand units!
        # NOTE: not randomly means from pre-determined data
        du = player.participant.treatment.get_demand(randomly=False, player=player)
        # order units
        ou = player.ou
        # stock units
        su = max(0, ou - du)

        # revenue = rcpu * min(du, ou)
        # cost = wcpu * ou + scpu * su
        # profit = revenue - cost
        revenue = rcpu * min(du, ou)
        cost = wcpu * ou + scpu * su
        profit = revenue - cost

        # update player su, du, revenue, cost, profit, & payoff
        player.su = su
        player.du = du
        player.revenue = Currency(revenue)
        player.cost = Currency(cost)
        player.profit = Currency(profit)
        player.payoff = player.participant.treatment.get_payoff(player)

        # update participant's history store corresponding to the current round in the current game
        real_round_number = get_real_round_number(player.round_number)
        idx = get_round_in_game(real_round_number) - 1
        hist = player.participant.history[idx]
        round_range = get_game_rounds(real_round_number)[0], player.round_number
        hist.update(
            ou=ou,
            du=du,
            su=su,
            ooq=player.ooq,
            revenue=float(revenue),
            cost=float(cost),
            profit=float(profit),
            cumulative_profit=float(sum(p.profit for p in player.in_rounds(*round_range))),
        )
        player.participant.history[idx] = hist


class Results(ShortHorizonPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number > C.PRACTICE_ROUNDS

    @staticmethod
    def before_next_page(player: Player, **kwargs) -> None:
        player.endtime = get_time()
        if player.round_number > C.PRACTICE_ROUNDS and is_game_over_round(player.round_number):
            # store game history & flush game state
            player.participant.game_results.append(player.participant.history)
            player.participant.history = initialize_game_history()


class ResultsFinal(ShortHorizonPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number > C.PRACTICE_ROUNDS and is_game_over_round(player.round_number)


class Payoff(ShortHorizonPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number > C.PRACTICE_ROUNDS and is_absolute_final_round(player.round_number)


# main sequence of pages for this otree app
# entire sequence is traversed every round
page_sequence = [
    HydratePlayer,
    Consent,
    Instructions1,
    Instructions2,
    Instructions3,
    PracticeDecide,
    PracticeResults,
    PracticeResultsFinal,
    Decide,
    Results,
    ResultsFinal,
    Payoff,
]
