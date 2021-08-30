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


author = 'Your name here'

doc = """
Choosing social media influencers (Knapsack problem)
"""


class Constants(BaseConstants):
    name_in_url = 'digitalmarketing'
    players_per_group = None
    num_rounds = 20
    names = ['@rainbowsalt',
             '@avocadopasta',
             '@livingdecora',
             '@miamicollective',
             '@velvetmoon',
             '@hifashiontaste',
             '@worknparty']


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    choices = models.StringField()