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

import numpy as np
import time

author = 'Your name here'

doc = """
Your app description
"""

t = 1000 * time.time() # current time in milliseconds
np.random.seed(int(t) % 2**32)


class Constants(BaseConstants):
    name_in_url = 'REItest'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            for p in self.get_players():
                t = 1000 * time.time() # current time in milliseconds
                p.participant.vars['seed1'] = int(t) % 2**32

            self.session.vars['endowment'] = self.session.config['endowment']
            self.session.vars['exchange'] = self.session.config['exchange']

            # self.session.vars['endowment'] = 25 # $ assigned in one part
            # self.session.vars['exchange'] = 5 # $/£

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # name = models.CharField()
    # email = models.CharField()
    # student_number = models.CharField()

    prolific_code = models.CharField()

    # The following section contians variables the CRT:
    # Both scores range between 0 - 7
    reflectiveness_score = models.IntegerField(initial=0)
    intuitiveness_score = models.IntegerField(initial=0)

    crt1 = models.StringField(widget = widgets.RadioSelect())

    def crt1_choices(self):
        np.random.seed(self.participant.vars['seed1'] + 1)
        choices = ['5 pence', '10 pence', '9 pence', '1 pence']
        np.random.shuffle(choices)
        return choices

    crt2 = models.StringField(widget = widgets.RadioSelect())

    def crt2_choices(self):
        np.random.seed(self.participant.vars['seed1'] + 2)
        choices = ['5 minutes', '100 minutes', '20 minutes', '500 minutes']
        np.random.shuffle(choices)
        return choices

    crt3 = models.StringField(widget = widgets.RadioSelect())

    def crt3_choices(self):
        np.random.seed(self.participant.vars['seed1'] + 3)
        choices = ['47 days', '24 days', '12 days', '36 days']
        np.random.shuffle(choices)
        return choices

    crt4 = models.StringField(widget = widgets.RadioSelect())

    def crt4_choices(self):
        np.random.seed(self.participant.vars['seed1'] + 4)
        choices = ['4 days', '9 days', '12 days', '3 days']
        np.random.shuffle(choices)
        return choices

    crt5 = models.StringField(widget = widgets.RadioSelect())

    def crt5_choices(self):
        np.random.seed(self.participant.vars['seed1'] + 5)
        choices = ['29 students', '30 students', '1 student', '15 students']
        np.random.shuffle(choices)
        return choices

    crt6 = models.StringField(widget = widgets.RadioSelect())

    def crt6_choices(self):
        np.random.seed(self.participant.vars['seed1'] + 6)
        choices = ['20 pounds', '10 pounds', '0 pounds', '30 pounds']
        np.random.shuffle(choices)
        return choices

    crt7 = models.StringField(widget = widgets.RadioSelect())

    def crt7_choices(self):
        np.random.seed(self.participant.vars['seed1'] + 7)
        choices = ['has lost money.', 'is ahead of where he began.', 'has broken even in the stock market.', 'it cannot be determined.']
        np.random.shuffle(choices)
        return choices

    # The following section contians variables for the BNT:
    # BNT score ranges between 0 - 4
    bnt_score = models.IntegerField(initial=0)

    bnt1 = models.StringField(widget = widgets.RadioSelect())

    def bnt1_choices(self):
        np.random.seed(self.participant.vars['seed1'] + 8)
        choices = ['5 out of 50 throws', '25 out of 50 throws', '30 out of 50 throws']
        np.random.shuffle(choices)
        choices = choices + ['None of the above']
        return choices

    bnt2 = models.StringField(widget = widgets.RadioSelect())

    def bnt2_choices(self):
        np.random.seed(self.participant.vars['seed1'] + 9)
        choices = ['10 %', '25 %', '40 %']
        np.random.shuffle(choices)
        choices = choices + ['None of the above']
        return choices

    bnt3 = models.StringField(widget = widgets.RadioSelect())

    def bnt3_choices(self):
        np.random.seed(self.participant.vars['seed1'] + 10)
        choices = ['20 out of 70 throws', '23 out of 70 throws', '35 out of 70 throws']
        np.random.shuffle(choices)
        choices = choices + ['None of the above']
        return choices

    bnt4 = models.StringField(widget = widgets.RadioSelect())

    def bnt4_choices(self):
        np.random.seed(self.participant.vars['seed1'] + 11)
        choices = ['4 %', '20 %', '50 %']
        np.random.shuffle(choices)
        choices = choices + ['None of the above']
        return choices

    # The following section contians variables for the NFC and FI survey
    nfcscore = models.PositiveIntegerField()
    fiscore = models.PositiveIntegerField()

    q1 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q2 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())

    q3 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q4 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q5 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q6 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q7 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q8 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q9 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q10 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q11 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q12 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q13 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q14 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q15 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q16 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q17 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q18 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q19 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q20 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q21 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q22 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q23 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q24 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q25 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q26 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q27 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q28 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q29 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q30 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q31 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    '''
    q32 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q33 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q34 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q35 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q36 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q37 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q38 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q39 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    q40 = models.PositiveIntegerField(
        choices = [[1,'1 = definitely not true'],[2, '2 = somewhat not true'],[3,'3 = neither true nor untrue'],[4,'4 = somewhat true'],[5,'5 = definitely true']], widget=widgets.RadioSelect())
    '''

    ### The section below contains variables for decition times

    dt_start = models.FloatField()
    dt_end = models.FloatField()

    dt_crt1 = models.FloatField()
    dt_crt2 = models.FloatField()
    dt_crt3 = models.FloatField()
    dt_crt4 = models.FloatField()
    dt_crt5 = models.FloatField()
    dt_crt6 = models.FloatField()
    dt_crt7 = models.FloatField()

    dt_bnt1 = models.FloatField()
    dt_bnt2 = models.FloatField()
    dt_bnt3 = models.FloatField()
    dt_bnt4 = models.FloatField()

    dt_rei = models.FloatField()
