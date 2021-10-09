from pathlib import Path

import pandas as pd
from otree.api import BaseGroup, BasePlayer, BaseSubsession
from otree.api import Currency as c
from otree.api import currency_range, models, widgets

from .constants import Constants
from .treatment import ALL_TREATMENT_GROUPS, DISRUPTION_CHOICES, VARIANCE_CHOICES


class Subsession(BaseSubsession):
    xyz = models.IntegerField()


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    ## keys
    participantid = models.StringField(label="Your participant ID:")
    starttime = models.FloatField()
    endtime = models.FloatField()
    starttime_iso = models.StringField()
    endtime_iso = models.StringField()

    ## session constants
    session_name_in_url = models.StringField(initial=Constants.name_in_url)
    session_num_rounds = models.IntegerField(initial=Constants.num_rounds)
    session_players_per_group = models.IntegerField(initial=Constants.players_per_group)
    session_endowment = models.CurrencyField(initial=Constants.endowment)

    ## participant treatment as serialized json string
    # NOTE: in roudn 1, assign to participant: player.participant.treatment = treatment.json(); reassign to player during each round thereafter to ensure propagation player.treatment = treatment.json()
    treatment = models.LongStringField()

    ## Game results
    orderquantity = models.PositiveIntegerField(choices=[0, 1, 2, 3, 4, 5, 6], widget=widgets.RadioSelect())

    trueorderquantity = models.PositiveIntegerField()

    formatted_payoff = models.StringField()

    check1low = models.PositiveIntegerField(
        choices=[[1, "936"], [2, "364"], [3, "858"]], widget=widgets.RadioSelect(), blank=True
    )
    check2low = models.PositiveIntegerField(
        choices=[[1, "0"], [2, "1/7"], [3, "5/7"]], widget=widgets.RadioSelect(), blank=True
    )
    check3low = models.PositiveIntegerField(
        choices=[[1, "5/7"], [2, "1/7"], [3, "2/7"]], widget=widgets.RadioSelect(), blank=True
    )
    check1high = models.PositiveIntegerField(
        choices=[[1, "560"], [2, "522"], [3, "662"]], widget=widgets.RadioSelect(), blank=True
    )
    check2high = models.PositiveIntegerField(
        choices=[[1, "0"], [2, "1/7"], [3, "5/7"]], widget=widgets.RadioSelect(), blank=True
    )
    check3high = models.PositiveIntegerField(
        choices=[[1, "5/7"], [2, "1/7"], [3, "2/7"]], widget=widgets.RadioSelect(), blank=True
    )
    check4 = models.PositiveIntegerField(
        choices=[[1, "Not all customers can be satisfied"], [2, "Nothing"], [3, "Not all items can be sold"]],
        widget=widgets.RadioSelect(),
        blank=True,
    )
    check5 = models.PositiveIntegerField(
        choices=[[1, "£0.11"], [2, "£11.30"], [3, "£1.13"]], widget=widgets.RadioSelect(), blank=True
    )
    pecu = models.PositiveIntegerField(
        choices=[
            [1, "1 = Not at all"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7"],
            [8, "8"],
            [9, "9 = As much as possible"],
        ],
        widget=widgets.RadioSelect(),
    )
    nonpecu = models.PositiveIntegerField(
        choices=[
            [1, "1 = Not at all"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7"],
            [8, "8"],
            [9, "9 = As much as possible"],
        ],
        widget=widgets.RadioSelect(),
    )
    conflict = models.PositiveIntegerField(
        choices=[
            [1, "1 = Least conflicted"],
            [2, "2"],
            [3, "3"],
            [4, "4"],
            [5, "5"],
            [6, "6"],
            [7, "7"],
            [8, "8"],
            [9, "9 = Most conflicted"],
        ],
        widget=widgets.RadioSelect(),
    )
