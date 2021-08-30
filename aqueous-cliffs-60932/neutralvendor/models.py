from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random, time, csv
from timeit import default_timer as timer


author = 'IL'

doc = """
Decision making between lotteries, parameters as in the Newsvendor game
"""


def profit(state, decision):

    if (state >= decision):
        prof = 7.28 * (decision*50+500) - 5.72 * (decision*50+500)
    else:
        prof = 7.28 * (state*50+500) - 5.72 * (decision*50+500)

    return prof


def set_time():

    timme = timer()

    return timme


def setdecision(decision):
    dec = ['A','B','C','D','E','F','G']
    val = dec[decision]

    return val


def setstate(state):
    dem = ['S1','S2','S3','S4','S5','S6','S7']
    val = dem[state]

    return val


class Constants(BaseConstants):

    name_in_url = 'neutralvendor'
    players_per_group = None
    num_rounds = 25
    endowment = None
    margin = 'low'


class Subsession(BaseSubsession):

    def before_session_starts(self):

        ifile = open('randomdemand.csv', 'rt')
        dema = []
        try:
            reader = csv.reader(ifile)
            for row in reader:
                dema.append(list(map(int, row)))
        finally:
            ifile.close()

        self.session.vars['state'] = dema[0]


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    starttime = models.FloatField()
    endtime = models.FloatField()
    decision = models.PositiveIntegerField(choices=[0, 1, 2, 3, 4, 5, 6], widget=widgets.RadioSelect())
    state = models.PositiveIntegerField()
    truestate = models.CharField()
    truedecision = models.CharField()
    check1 = models.PositiveIntegerField(
        choices=[[1, '936'], [2, '364'], [3, '858']], widget=widgets.RadioSelect(), blank=True)
    check2 = models.PositiveIntegerField(
        choices=[[1, '0'], [2, '1/7'], [3, '5/7']], widget=widgets.RadioSelect(), blank=True)
    check3 = models.PositiveIntegerField(
        choices=[[1, '5/7'], [2, '1/7'], [3, '2/7']], widget=widgets.RadioSelect(), blank=True)
    check4 = models.PositiveIntegerField(
        choices=[[1, '1/7'], [2, '0'], [3, '5/7']], widget=widgets.RadioSelect(), blank=True)
    check5 = models.PositiveIntegerField(
        choices=[[1, '£0.11'], [2, '£11.30'], [3, '£1.13']], widget=widgets.RadioSelect(), blank=True)
