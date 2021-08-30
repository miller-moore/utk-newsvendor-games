from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import time
from random import randint
from timeit import default_timer as timer
import csv


doc = """
Continuation for those players who have already played nvcompnoniid, no test questions
"""


def marketinfo():
    allq = []
    with open('marketdata2.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            allq.append(int(row[2]))

    return (allq)


def owninfo(prolificcode):
    with open('marketdata2.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if row[0] == prolificcode:
                ownq = int(row[2])
                othq = int(row[3])
                dem = int(row[4])

    if ownq > othq:
        efd = dem / 2 + max(dem / 2 - othq, 0)
        efd2 = dem / 2
    else:
        efd = dem / 2
        efd2 = dem / 2 + max(dem / 2 - ownq, 0)

    ownpay = int(4 * min(efd, ownq) - 2 * ownq)
    othpay = int(4 * min(efd2, othq) - 2 * othq)

    return [ownq, othq, dem, ownpay, othpay]


def codenotexist(prolificcode):

    notexist = 1

    with open('marketdata2.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if row[0] == prolificcode:
                notexist = 0

    return notexist


def set_time():

    timme = timer()

    return timme


def set_demand():

    demand = 2*randint(1,100)

    return demand


class Constants(BaseConstants):
    name_in_url = 'nvcompnoniid2'
    players_per_group = 2
    num_rounds = 1
    price = 4
    cost = 2
    instructions_template = 'nvcompnoniid2/Instructions.html'
    profitcalculator_template = 'nvcompnoniid2/profitcalculator2.html'
    marketinfo_template = 'nvcompnoniid2/Marketinformation.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    demand = models.PositiveIntegerField()


class Player(BasePlayer):

    prolificcode = models.CharField()

    othpayoff = models.IntegerField()
    starttime = models.FloatField()
    endtime = models.FloatField()
    units = models.PositiveIntegerField(
        min=1, max=100,
        doc="""Quantity of units to order"""
    )

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
