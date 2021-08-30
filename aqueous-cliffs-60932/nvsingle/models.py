from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import time
from random import randint
from timeit import default_timer as timer


doc = """
NV monopoly
"""


def set_time():

    timme = timer()

    return timme


def set_demand():

    demand = randint(1,100)

    return demand


class Constants(BaseConstants):
    name_in_url = 'nvsingle'
    players_per_group = None
    num_rounds = 1
    price = 4
    cost = 2
    instructions_template = 'nvsingle/Instructions.html'
    profitcalculator = 'nvsingle/profitcalculator2.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    starttime = models.FloatField()
    endtime = models.FloatField()
    demand = models.PositiveIntegerField()
    units = models.PositiveIntegerField(
        min=1, max=100,
        doc="""Quantity of units to order"""
    )

    qu1 = models.PositiveIntegerField(
        choices=[45, 100, 90], widget=widgets.RadioSelect(), blank=True)
    qu2 = models.PositiveIntegerField(
        choices=[100, 140, 200], widget=widgets.RadioSelect(), blank=True)
    qu3 = models.PositiveIntegerField(
        choices=[40, 60, 100], widget=widgets.RadioSelect(), blank=True)

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):

        q = self.units
        d = self.demand

        if (q < d):
            self.payoff = Constants.price * q - Constants.cost * q
        else:
            self.payoff = Constants.price * d - Constants.cost * q
