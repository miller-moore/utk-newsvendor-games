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
Deming''s funnel expreriment for OM students
"""


class Constants(BaseConstants):
    name_in_url = 'funnel'
    players_per_group = None
    num_rounds = 40
    instructions_template = 'funnel/Instructions.html'
    stdev = 30 # standard deviation for marble location


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    x = models.IntegerField()
    y = models.IntegerField()
    xcoord = models.IntegerField()
    ycoord = models.IntegerField()
    score = models.FloatField()
