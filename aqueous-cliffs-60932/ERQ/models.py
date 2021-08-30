from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

author = 'IL'

doc = """Emotion Regulation Questionnaire"""


class Constants(BaseConstants):
    name_in_url = 'ERQ'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    q1 = models.PositiveIntegerField(choices = [[1,'1 = strongly disagree'],[2, '2 = moderately disagree'],[3,'3 = somewhat disagree'],[4,'4 = not sure'],[5,'5 = somewhat agree'],[6,'6 = moderately agree'],[7,'7 = strongly agree']], widget=widgets.RadioSelect())
    q2 = models.PositiveIntegerField(choices = [[1,'1 = strongly disagree'],[2, '2 = moderately disagree'],[3,'3 = somewhat disagree'],[4,'4 = not sure'],[5,'5 = somewhat agree'],[6,'6 = moderately agree'],[7,'7 = strongly agree']], widget=widgets.RadioSelect())
    q3 = models.PositiveIntegerField(choices = [[1,'1 = strongly disagree'],[2, '2 = moderately disagree'],[3,'3 = somewhat disagree'],[4,'4 = not sure'],[5,'5 = somewhat agree'],[6,'6 = moderately agree'],[7,'7 = strongly agree']], widget=widgets.RadioSelect())
    q4 = models.PositiveIntegerField(choices = [[1,'1 = strongly disagree'],[2, '2 = moderately disagree'],[3,'3 = somewhat disagree'],[4,'4 = not sure'],[5,'5 = somewhat agree'],[6,'6 = moderately agree'],[7,'7 = strongly agree']], widget=widgets.RadioSelect())
    q5 = models.PositiveIntegerField(choices = [[1,'1 = strongly disagree'],[2, '2 = moderately disagree'],[3,'3 = somewhat disagree'],[4,'4 = not sure'],[5,'5 = somewhat agree'],[6,'6 = moderately agree'],[7,'7 = strongly agree']], widget=widgets.RadioSelect())
    q6 = models.PositiveIntegerField(choices = [[1,'1 = strongly disagree'],[2, '2 = moderately disagree'],[3,'3 = somewhat disagree'],[4,'4 = not sure'],[5,'5 = somewhat agree'],[6,'6 = moderately agree'],[7,'7 = strongly agree']], widget=widgets.RadioSelect())
    q7 = models.PositiveIntegerField(choices = [[1,'1 = strongly disagree'],[2, '2 = moderately disagree'],[3,'3 = somewhat disagree'],[4,'4 = not sure'],[5,'5 = somewhat agree'],[6,'6 = moderately agree'],[7,'7 = strongly agree']], widget=widgets.RadioSelect())
    q8 = models.PositiveIntegerField(choices = [[1,'1 = strongly disagree'],[2, '2 = moderately disagree'],[3,'3 = somewhat disagree'],[4,'4 = not sure'],[5,'5 = somewhat agree'],[6,'6 = moderately agree'],[7,'7 = strongly agree']], widget=widgets.RadioSelect())
    q9 = models.PositiveIntegerField(choices = [[1,'1 = strongly disagree'],[2, '2 = moderately disagree'],[3,'3 = somewhat disagree'],[4,'4 = not sure'],[5,'5 = somewhat agree'],[6,'6 = moderately agree'],[7,'7 = strongly agree']], widget=widgets.RadioSelect())
    q10 = models.PositiveIntegerField(choices = [[1,'1 = strongly disagree'],[2, '2 = moderately disagree'],[3,'3 = somewhat disagree'],[4,'4 = not sure'],[5,'5 = somewhat agree'],[6,'6 = moderately agree'],[7,'7 = strongly agree']], widget=widgets.RadioSelect())
