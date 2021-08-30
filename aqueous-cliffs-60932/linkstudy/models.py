from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Your name here'

doc = """
Link study
"""


class Constants(BaseConstants):
    name_in_url = 'linkstudy'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    code = models.CharField()
    q1 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q2 = models.PositiveIntegerField(
        choices = [[0,'Yes'],[1, 'No']], widget=widgets.RadioSelectHorizontal())
    q3 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q4 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q5 = models.PositiveIntegerField(
        choices = [[0,'Yes'],[1, 'No']], widget=widgets.RadioSelectHorizontal())
    q6 = models.PositiveIntegerField(
        choices = [[0,'Yes'],[1, 'No']], widget=widgets.RadioSelectHorizontal())
    q7 = models.PositiveIntegerField(
        choices = [[0,'Yes'],[1, 'No']], widget=widgets.RadioSelectHorizontal())
    q8 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q9 = models.PositiveIntegerField(
        choices = [[0,'Yes'],[1, 'No']], widget=widgets.RadioSelectHorizontal())
    q10 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q11 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q12 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q13 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q14 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q15 = models.PositiveIntegerField(
        choices = [[0,'Yes'],[1, 'No']], widget=widgets.RadioSelectHorizontal())
    q16 = models.PositiveIntegerField(
        choices = [[0,'Yes'],[1, 'No']], widget=widgets.RadioSelectHorizontal())
    q17 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q18 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q19 = models.PositiveIntegerField(
        choices = [[0,'Yes'],[1, 'No']], widget=widgets.RadioSelectHorizontal())
    q20 = models.PositiveIntegerField(
        choices = [[1,'Yes'],[0, 'No']], widget=widgets.RadioSelectHorizontal())
    q21 = models.PositiveIntegerField(
        choices = [[0,'Yes'],[1, 'No']], widget=widgets.RadioSelectHorizontal())
    q22 = models.PositiveIntegerField(
        choices = [[1,'(A)'],[2,'(B)']], widget=widgets.RadioSelect())
    conflict22 = models.PositiveIntegerField(
        choices = [1,2,3,4,5,6,7,8,9], widget=widgets.RadioSelectHorizontal())
    q23 = models.PositiveIntegerField(
        choices = [[1,'(A)'],[2,'(B)']], widget=widgets.RadioSelect())
    conflict23 = models.PositiveIntegerField(
        choices = [1,2,3,4,5,6,7,8,9], widget=widgets.RadioSelectHorizontal())
    q24 = models.PositiveIntegerField(
        choices = [[1,'(A)'],[2,'(B)']], widget=widgets.RadioSelect())
    conflict24 = models.PositiveIntegerField(
        choices = [1,2,3,4,5,6,7,8,9], widget=widgets.RadioSelectHorizontal())
    q25 = models.PositiveIntegerField(
        choices = [[1,'(A)'],[2,'(B)']], widget=widgets.RadioSelect())
    conflict25 = models.PositiveIntegerField(
        choices = [1,2,3,4,5,6,7,8,9], widget=widgets.RadioSelectHorizontal())
    q26 = models.PositiveIntegerField(
        choices = [[1,'(A)'],[2,'(B)']], widget=widgets.RadioSelect())
    conflict26 = models.PositiveIntegerField(
        choices = [1,2,3,4,5,6,7,8,9], widget=widgets.RadioSelectHorizontal())
    q27 = models.PositiveIntegerField(
        choices = [[1,'(A)'],[2,'(B)']], widget=widgets.RadioSelect())
    conflict27 = models.PositiveIntegerField(
        choices = [1,2,3,4,5,6,7,8,9], widget=widgets.RadioSelectHorizontal())