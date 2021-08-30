from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Ilkka Leppanen'

doc = """
Digital Marketing -- 0/1 Knapsack problem
"""


class Constants(BaseConstants):
    name_in_url = 'digitalmarketing'
    players_per_group = None
    num_rounds = 100


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    shoes = models.StringField(choices=['IG1','IG2','IG3','IG4'], widget=widgets.RadioSelect)
    handbag = models.StringField(choices=['IG1','IG2','IG3','IG4'], widget=widgets.RadioSelect)