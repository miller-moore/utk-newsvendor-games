from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Ilkka Leppanen'

doc = """
Dating App -- Matching problem
"""


class Constants(BaseConstants):
    name_in_url = 'datingapp'
    players_per_group = None
    num_rounds = 20


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    name = models.StringField()
    Chloe = models.StringField(blank=True)
    Emily = models.StringField(blank=True)
    Megan = models.StringField(blank=True)
    Charlotte = models.StringField(blank=True)
    Jessica = models.StringField(blank=True)
    Lauren = models.StringField(blank=True)
    Sophie = models.StringField(blank=True)
    Olivia = models.StringField(blank=True)
    Hannah = models.StringField(blank=True)
    Lucy = models.StringField(blank=True)