from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

author = 'IL'

doc = """Survey combining DSR (13+12 questions) and AQ (29 questions)"""


class Constants(BaseConstants):
    name_in_url = 'dsraq'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    aq1 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq2 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq3 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq4 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq5 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq6 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq7 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq8 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq9 = models.PositiveIntegerField(choices=[5,4,3,2,1], widget=widgets.RadioSelectHorizontal())
    aq10 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq11 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq12 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq13 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq14 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq15 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq16 = models.PositiveIntegerField(choices=[5,4,3,2,1], widget=widgets.RadioSelectHorizontal())
    aq17 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq18 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq19 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq20 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq21 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq22 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq23 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq24 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq25 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq26 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq27 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq28 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())
    aq29 = models.PositiveIntegerField(choices=[1,2,3,4,5], widget=widgets.RadioSelectHorizontal())

    dsr1 = models.PositiveIntegerField(choices=[[1,'F'],[0,'T']], widget=widgets.RadioSelectHorizontal())
    dsr2 = models.PositiveIntegerField(choices=[[0,'F'],[1,'T']], widget=widgets.RadioSelectHorizontal())
    dsr3 = models.PositiveIntegerField(choices=[[1,'F'],[0,'T']], widget=widgets.RadioSelectHorizontal())
    dsr4 = models.PositiveIntegerField(choices=[[0,'F'],[1,'T']], widget=widgets.RadioSelectHorizontal())
    dsr5 = models.PositiveIntegerField(choices=[[0,'F'],[1,'T']], widget=widgets.RadioSelectHorizontal())
    dsr6 = models.PositiveIntegerField(choices=[[0,'F'],[1,'T']], widget=widgets.RadioSelectHorizontal())
    dsr7 = models.PositiveIntegerField(choices=[[1,'F'],[0,'T']], widget=widgets.RadioSelectHorizontal())
    dsr8 = models.PositiveIntegerField(choices=[[0,'F'],[1,'T']], widget=widgets.RadioSelectHorizontal())
    dsr9 = models.PositiveIntegerField(choices=[[0,'F'],[1,'T']], widget=widgets.RadioSelectHorizontal())
    dsr10 = models.PositiveIntegerField(choices=[[0,'F'],[1,'T']], widget=widgets.RadioSelectHorizontal())
    dsr11 = models.PositiveIntegerField(choices=[[0,'F'],[1,'T']], widget=widgets.RadioSelectHorizontal())
    dsr12 = models.PositiveIntegerField(choices=[[0,'F'],[1,'T']], widget=widgets.RadioSelectHorizontal())
    dsr13 = models.PositiveIntegerField(choices=[[0,'F'],[1,'T']], widget=widgets.RadioSelectHorizontal())

    dsr14 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
    dsr15 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
    dsr16 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
    dsr17 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
    dsr18 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
    dsr19 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
    dsr20 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
    dsr21 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
    dsr22 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
    dsr23 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
    dsr24 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
    dsr25 = models.FloatField(choices=[[0,'1'],[0.5,'2'],[1,'3']], widget=widgets.RadioSelectHorizontal())
