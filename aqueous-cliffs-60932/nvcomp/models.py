from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import time
from random import randint
from timeit import default_timer as timer


doc = """
NV competition with independent demands
"""


def set_time():

    timme = timer()

    return timme


def set_demand():

    demand = randint(1,100)

    return demand


class Constants(BaseConstants):
    name_in_url = 'nvcomp'
    players_per_group = 2
    num_rounds = 1
    price = 4
    cost = 2
    instructions_template = 'nvcomp/Instructions.html'
    profitcalculator_template = 'nvcomp/profitcalculator2.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    othpayoff = models.IntegerField()
    starttime = models.FloatField()
    endtime = models.FloatField()
    demand = models.PositiveIntegerField()
    units = models.PositiveIntegerField(
        min=1, max=100,
        doc="""Quantity of units to order"""
    )

    qu1 = models.PositiveIntegerField(
        choices=[66, 14, 41], widget=widgets.RadioSelect(), blank=True)
    qu2 = models.PositiveIntegerField(
        choices=[50, 82, 10], widget=widgets.RadioSelect(), blank=True)
    qu3 = models.PositiveIntegerField(
        choices=[300, 280, 100], widget=widgets.RadioSelect(), blank=True)

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):

        q1 = self.units
        q2 = self.other_player().units
        d1 = self.demand
        d2 = self.other_player().demand

        if (q2 < d2):
            efdemand = d1 + int(round(0.8*(d2 - q2)))
        else:
            efdemand = d1

        if (q1 > efdemand):
            self.payoff = Constants.price * efdemand - Constants.cost * q1
        else:
            self.payoff = Constants.price * q1 - Constants.cost * q1


        if (q1 < d1):
            efdemand2 = d2 + int(round(0.8*(d1 - q1)))
        else:
            efdemand2 = d2

        if (q2 > efdemand2):
            self.othpayoff = Constants.price * efdemand2 - Constants.cost * q2
        else:
            self.othpayoff = Constants.price * q2 - Constants.cost * q2
