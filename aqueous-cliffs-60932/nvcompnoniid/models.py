from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import time
from random import randint
from timeit import default_timer as timer


doc = """
NV competition with common industry demand split in half
"""


def set_time():

    timme = timer()

    return timme


def set_demand():

    demand = 2*randint(1,100)

    return demand


class Constants(BaseConstants):
    name_in_url = 'nvcompnoniid'
    players_per_group = 2
    num_rounds = 1
    price = 4
    cost = 2
    instructions_template = 'nvcompnoniid/Instructions.html'
    profitcalculator_template = 'nvcompnoniid/profitcalculator2.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    demand = models.PositiveIntegerField()


class Player(BasePlayer):

    othpayoff = models.IntegerField()
    starttime = models.FloatField()
    endtime = models.FloatField()
    units = models.PositiveIntegerField(
        min=1, max=100,
        doc="""Quantity of units to order"""
    )

    qu1 = models.PositiveIntegerField(
        choices=[86, 70, 40], widget=widgets.RadioSelect(), blank=True)
    qu2 = models.PositiveIntegerField(
        choices=[0, 50, 25], widget=widgets.RadioSelect(), blank=True)
    qu3 = models.PositiveIntegerField(
        choices=[320, 240, 280], widget=widgets.RadioSelect(), blank=True)

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):

        q1 = self.units
        q2 = self.other_player().units
        d = self.group.demand

        if (q1 > q2):
            self.payoff = Constants.price * min(d/2 + max(int(round(0.8*(d/2 - q2))), 0), q1) - Constants.cost * q1
        else:
            self.payoff = Constants.price * min(d/2, q1) - Constants.cost * q1

        if (q2 > q1):
            self.othpayoff = Constants.price * min(d/2 + max(int(round(0.8*(d/2 - q1))), 0), q2) - Constants.cost * q2
        else:
            self.othpayoff = Constants.price * min(d/2, q2) - Constants.cost * q2
