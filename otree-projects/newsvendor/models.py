import csv
import random
import time
from pathlib import Path
from timeit import default_timer as timer

import pandas as pd
from otree.api import BaseConstants, BaseGroup, BasePlayer, BaseSubsession
from otree.api import Currency as c
from otree.api import currency_range, models, widgets

author = "IL"

doc = """
Newsvendor game
Payoffs given in a payoff table
High and low variance treatments
"""

PATH = Path(__file__).resolve()


def randomdemand(variance_option):
    if variance_option == "low":
        return random.gauss(500, 50)
    return random.gauss(300, 100)


def trueorderquantity(orderquantity, variance_option):

    if variance_option == "low":
        toq = 500 + orderquantity * 50
    else:
        toq = 300 + orderquantity * 100

    return toq


def profit(demand, orderquantity, variance_option):

    toq = trueorderquantity(orderquantity, variance_option)

    if variance_option == "low":
        if demand >= toq:
            prof = 7.28 * toq - 5.72 * toq
        else:
            prof = 7.28 * demand - 5.72 * toq

    else:
        if demand >= toq:
            prof = 1.78 * toq - 0.38 * toq
        else:
            prof = 1.78 * demand - 0.38 * toq

    return prof


def set_time():

    timme = timer()

    return timme


class Constants(BaseConstants):

    name_in_url = "newsvendor"
    players_per_group = None
    num_rounds = 25
    endowment = None


class Subsession(BaseSubsession):
    @staticmethod
    def creating_session(subsession):

        # ifile = open(PATH.parent / "randomdemand.csv", "rt")
        # dema = []
        # try:
        #     reader = csv.reader(ifile)
        #     for row in reader:
        #         dema.append(list(map(int, row)))
        # finally:
        #     ifile.close()

        # if subsession.session.config["variance_option"] == "low":
        #     subsession.session.vars["demand"] = dema[0]

        # else:
        #     subsession.session.vars["demand"] = dema[1]

        demand_df = pd.read_csv(PATH.parent / "static" / "demand_distributions.csv")

        if subsession.session.config["variance_option"] == "low":
            subsession.session.vars["demand"] = demand_df.d1.values.tolist()

        else:
            subsession.session.vars["demand"] = demand_df.d2.values.tolist()


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    prolificcode = models.CharField()
    starttime = models.FloatField()
    endtime = models.FloatField()
    orderquantity = models.PositiveIntegerField(choices=[0, 1, 2, 3, 4, 5, 6], widget=widgets.RadioSelect())
    trueorderquantity = models.PositiveIntegerField()
    formatted_payoff = models.StringField()
    demand = models.PositiveIntegerField()
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
