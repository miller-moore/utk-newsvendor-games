from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)

from timeit import default_timer as timer


author = 'Your name here'

doc = """
Your app description
"""


def set_time():

    time_now = timer()

    return time_now


class Constants(BaseConstants):
    name_in_url = 'testform'
    players_per_group = None
    num_rounds = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    choice = models.StringField()
    dectime = models.FloatField()
    jsdectime_start = models.FloatField() # dectime with the JS method
    jsdectime_end = models.FloatField() # dectime with the JS method
    afterpage_time = models.FloatField() # this is recorded only for testing purposes, not needed in the final app