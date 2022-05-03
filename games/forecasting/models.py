import random
import types
from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid4

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models, widgets
from otree.currency import Currency
from otree.models.participant import Participant

from .constants import C
from .treatment import PracticeTreatmentId, Treatment, UnitCosts
from .util import get_game_number, get_game_rounds, get_round_in_game, get_time

from common.template_filters import filters  # isort:skip


class Subsession(BaseSubsession):
    pass
    # is_practice_round = models.BooleanField()
    # real_round_number = models.IntegerField()

    # def vars_for_admin_report(self):
    #     """See https://otree.readthedocs.io/en/self/admin.html#customizing-the-admin-interface-admin-reports"""
    #     payoffs = sorted([p.payoff for p in self.get_players()])
    #     return dict(payoffs=payoffs)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # identifiers
    uuid = models.StringField()
    starttime = models.FloatField(min=get_time())
    endtime = models.FloatField(min=get_time())
    treatment_id = models.IntegerField(min=1)
    practice_treatment_id = models.IntegerField(choices=list(PracticeTreatmentId))

    # Consent.html form fields
    is_planner = models.BooleanField(
        widget=widgets.RadioSelectHorizontal(),
        label="""Are you presently either a Junior or Senior undergraduate or graduate student studying Supply Chain Management or another related field?""",
    )
    gender_identity = models.StringField(
        label="If willing, please type your Gender Identity in the box below.", initial=None, blank=True
    )
    does_consent = models.BooleanField(
        widget=widgets.CheckboxInput(),
        label="""By checking the box to the left you agree to participate in this experiment.""",
    )

    # player data
    game_number = models.IntegerField(min=1, initial=1)
    period_number = models.IntegerField(min=1, initial=1)

    # demand units, stock units, & order units (see Decide.html)
    du = models.IntegerField(min=0)
    su = models.IntegerField(min=0, initial=0)
    ou = models.IntegerField(
        min=0,
        max=1000,
        # label="How many units will you order?"
    )  # Decide.html

    # Optimal order quantity (see treatment.py)
    ooq = models.IntegerField(min=0)

    # Unit prices: retail price (revenue), wholesale price (cost), salvage price (cost)
    rcpu = models.CurrencyField()
    wcpu = models.CurrencyField()
    scpu = models.CurrencyField()

    # NOTE: revenue, cost, and profit fields are calculated in method `Decide.before_next_page` (pages.py:238)
    revenue = models.CurrencyField(initial=0)
    cost = models.CurrencyField(initial=0)
    profit = models.CurrencyField(initial=0)

    payoff_round = models.IntegerField()
