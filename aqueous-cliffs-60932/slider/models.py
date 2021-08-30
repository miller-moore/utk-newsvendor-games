from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import random, time, csv
from timeit import default_timer as timer

author = 'Your name here'

doc = """
Newsvendor with slider selection
Profits as in Schweitzer and Cachon, q between 1 and 300
"""

def profit(d, q, margin):

    if (margin == 'low'):
        if (d >= q):
            prof = 12 * q - 9 * q
        else:
            prof = 12 * d - 9 * q

    else:
        if (d >= q):
            prof = 12 * q - 3 * q
        else:
            prof = 12 * d - 3 * q

    return prof


def revenue(d, q):

    if (d >= q):
        rev = 12 * q
    else:
        rev = 12 * d

    return rev


def cost(q, margin):

    if (margin == 'low'):
        costi = 9 * q
    else:
        costi = 3 * q
    return costi


def set_time():

    timme = timer()

    return timme


class Constants(BaseConstants):
    name_in_url = 'slider'
    players_per_group = None
    num_rounds = 30 # 15 high margin and 15 low margin
    instructions_template = 'slider/Instructions.html'
    profitcalculator_template = 'slider/profitcalculator2.html'


class Subsession(BaseSubsession):

    def creating_session(self):

        # demand must be uniform between 1 and 300
        ifile = open('randomdemand2.csv', 'rt')
        dema = []
        try:
            reader = csv.reader(ifile)
            for row in reader:
                dema.append(list(map(int, row)))
        finally:
            ifile.close()

        # here low and high margin have same demand distributions
        self.session.vars['d'] = dema[0]


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    starttime = models.FloatField()
    endtime = models.FloatField()
    q = models.IntegerField()
    d = models.IntegerField()
    revenue = models.IntegerField()
    cost = models.IntegerField()