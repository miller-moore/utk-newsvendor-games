from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Your name here'

doc = """
Allport value scale survey
"""


class Constants(BaseConstants):
    name_in_url = 'allport'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    name = models.CharField()
    email = models.CharField()
    q1a = models.PositiveIntegerField(choices=[0,1,2,3])
    q1b = models.PositiveIntegerField(choices=[0,1,2,3])
    q2a = models.PositiveIntegerField(choices=[0,1,2,3])
    q2b = models.PositiveIntegerField(choices=[0,1,2,3])
    q3a = models.PositiveIntegerField(choices=[0,1,2,3])
    q3b = models.PositiveIntegerField(choices=[0,1,2,3])
    q4a = models.PositiveIntegerField(choices=[0,1,2,3])
    q4b = models.PositiveIntegerField(choices=[0,1,2,3])
    q5a = models.PositiveIntegerField(choices=[0,1,2,3])
    q5b = models.PositiveIntegerField(choices=[0,1,2,3])
    q6a = models.PositiveIntegerField(choices=[0,1,2,3])
    q6b = models.PositiveIntegerField(choices=[0,1,2,3])
    q7a = models.PositiveIntegerField(choices=[0,1,2,3])
    q7b = models.PositiveIntegerField(choices=[0,1,2,3])
    q8a = models.PositiveIntegerField(choices=[0,1,2,3])
    q8b = models.PositiveIntegerField(choices=[0,1,2,3])
    q9a = models.PositiveIntegerField(choices=[0,1,2,3])
    q9b = models.PositiveIntegerField(choices=[0,1,2,3])
    q10a = models.PositiveIntegerField(choices=[0,1,2,3])
    q10b = models.PositiveIntegerField(choices=[0,1,2,3])

    q11a = models.PositiveIntegerField(choices=[0,1,2,3])
    q11b = models.PositiveIntegerField(choices=[0,1,2,3])
    q12a = models.PositiveIntegerField(choices=[0,1,2,3])
    q12b = models.PositiveIntegerField(choices=[0,1,2,3])
    q13a = models.PositiveIntegerField(choices=[0,1,2,3])
    q13b = models.PositiveIntegerField(choices=[0,1,2,3])
    q14a = models.PositiveIntegerField(choices=[0,1,2,3])
    q14b = models.PositiveIntegerField(choices=[0,1,2,3])
    q15a = models.PositiveIntegerField(choices=[0,1,2,3])
    q15b = models.PositiveIntegerField(choices=[0,1,2,3])
    q16a = models.PositiveIntegerField(choices=[0,1,2,3])
    q16b = models.PositiveIntegerField(choices=[0,1,2,3])
    q17a = models.PositiveIntegerField(choices=[0,1,2,3])
    q17b = models.PositiveIntegerField(choices=[0,1,2,3])
    q18a = models.PositiveIntegerField(choices=[0,1,2,3])
    q18b = models.PositiveIntegerField(choices=[0,1,2,3])
    q19a = models.PositiveIntegerField(choices=[0,1,2,3])
    q19b = models.PositiveIntegerField(choices=[0,1,2,3])
    q20a = models.PositiveIntegerField(choices=[0,1,2,3])
    q20b = models.PositiveIntegerField(choices=[0,1,2,3])

    q21a = models.PositiveIntegerField(choices=[0,1,2,3])
    q21b = models.PositiveIntegerField(choices=[0,1,2,3])
    q22a = models.PositiveIntegerField(choices=[0,1,2,3])
    q22b = models.PositiveIntegerField(choices=[0,1,2,3])
    q23a = models.PositiveIntegerField(choices=[0,1,2,3])
    q23b = models.PositiveIntegerField(choices=[0,1,2,3])
    q24a = models.PositiveIntegerField(choices=[0,1,2,3])
    q24b = models.PositiveIntegerField(choices=[0,1,2,3])
    q25a = models.PositiveIntegerField(choices=[0,1,2,3])
    q25b = models.PositiveIntegerField(choices=[0,1,2,3])
    q26a = models.PositiveIntegerField(choices=[0,1,2,3])
    q26b = models.PositiveIntegerField(choices=[0,1,2,3])
    q27a = models.PositiveIntegerField(choices=[0,1,2,3])
    q27b = models.PositiveIntegerField(choices=[0,1,2,3])
    q28a = models.PositiveIntegerField(choices=[0,1,2,3])
    q28b = models.PositiveIntegerField(choices=[0,1,2,3])
    q29a = models.PositiveIntegerField(choices=[0,1,2,3])
    q29b = models.PositiveIntegerField(choices=[0,1,2,3])
    q30a = models.PositiveIntegerField(choices=[0,1,2,3])
    q30b = models.PositiveIntegerField(choices=[0,1,2,3])

    qq1a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq1b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq1c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq1d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq2a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq2b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq2c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq2d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq3a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq3b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq3c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq3d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq4a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq4b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq4c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq4d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq5a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq5b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq5c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq5d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq6a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq6b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq6c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq6d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq7a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq7b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq7c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq7d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq8a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq8b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq8c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq8d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq9a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq9b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq9c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq9d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq10a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq10b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq10c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq10d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq11a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq11b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq11c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq11d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq12a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq12b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq12c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq12d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq13a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq13b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq13c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq13d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq14a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq14b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq14c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq14d = models.PositiveIntegerField(choices=[1,2,3,4])

    qq15a = models.PositiveIntegerField(choices=[1,2,3,4])
    qq15b = models.PositiveIntegerField(choices=[1,2,3,4])
    qq15c = models.PositiveIntegerField(choices=[1,2,3,4])
    qq15d = models.PositiveIntegerField(choices=[1,2,3,4])