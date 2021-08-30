from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Ilkka Leppanen'

doc = """
This is the landing page for Business Analytics Challenges
"""


class Constants(BaseConstants):
    name_in_url = 'bachallenge'
    players_per_group = None
    num_rounds = 100


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    name = models.StringField()
    appchoice = models.StringField(choices=['Dating App','Digital Marketing', 'Moonrover'])