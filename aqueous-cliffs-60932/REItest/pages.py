from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants

import time
import numpy as np

class Consent(Page):
    form_model = models.Player
    form_fields = ['prolific_code']


class Introduction(Page):

    def vars_for_template(self):

        endowment = self.session.vars['endowment']
        exchange = self.session.vars['exchange']
        pound = endowment / exchange

        if pound.is_integer():
            pound = int(pound)

        pound_total = pound * 2

        return {
            'endowment': '$' + str(endowment),
            'exchange': exchange,
            'pound': '£' + str(pound),
            'pound_total': '£' + str(pound_total)
        }

""" CRT """
class CRT1page(Page):
    form_model = models.Player
    form_fields = ['crt1', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT1page) + 1
        return {
            's1_total': s1_total,
            'number': number
        }

    def before_next_page(self):
        if self.player.crt1 == '5 pence':
            self.player.reflectiveness_score += 1
        elif self.player.crt1 == '10 pence':
            self.player.intuitiveness_score += 1

        self.player.dt_crt1 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT2page(Page):
    form_model = models.Player
    form_fields = ['crt2', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT2page) + 1
        return {
            's1_total': s1_total,
            'number': number
        }

    def before_next_page(self):
        if self.player.crt2 == '5 minutes':
            self.player.reflectiveness_score += 1
        elif self.player.crt2 == '100 minutes':
            self.player.intuitiveness_score += 1

        self.player.dt_crt2 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT3page(Page):
    form_model = models.Player
    form_fields = ['crt3', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT3page) + 1
        return {
            's1_total': s1_total,
            'number': number
        }

    def before_next_page(self):
        if self.player.crt3 == '47 days':
            self.player.reflectiveness_score += 1
        elif self.player.crt3 == '24 days':
            self.player.intuitiveness_score += 1

        self.player.dt_crt3 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT4page(Page):
    form_model = models.Player
    form_fields = ['crt4', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT4page) + 1
        return {
            's1_total': s1_total,
            'number': number
        }

    def before_next_page(self):
        if self.player.crt4 == '4 days':
            self.player.reflectiveness_score += 1
        elif self.player.crt4 == '9 days':
            self.player.intuitiveness_score += 1

        self.player.dt_crt4 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT5page(Page):
    form_model = models.Player
    form_fields = ['crt5', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT5page) + 1
        return {
            's1_total': s1_total,
            'number': number
        }

    def before_next_page(self):
        if self.player.crt5 == '29 students':
            self.player.reflectiveness_score += 1
        elif self.player.crt5 == '30 students':
            self.player.intuitiveness_score += 1

        self.player.dt_crt5 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT6page(Page):
    form_model = models.Player
    form_fields = ['crt6', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT6page) + 1
        return {
            's1_total': s1_total,
            'number': number
        }

    def before_next_page(self):
        if self.player.crt6 == '20 pounds':
            self.player.reflectiveness_score += 1
        elif self.player.crt6 == '10 pounds':
            self.player.intuitiveness_score += 1

        self.player.dt_crt6 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT7page(Page):
    form_model = models.Player
    form_fields = ['crt7', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT7page) + 1
        return {
            's1_total': s1_total,
            'number': number
        }

    def before_next_page(self):
        if self.player.crt7 == 'has lost money.':
            self.player.reflectiveness_score += 1
        elif self.player.crt7 == 'is ahead of where he began.':
            self.player.intuitiveness_score += 1

        self.player.dt_crt7 = (self.player.dt_end - self.player.dt_start) / 1000


""" BNT """
class BNT1page(Page):
    form_model = models.Player
    form_fields = ['bnt1', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = BNT_seq.index(BNT1page) + 1 + len(CRT_seq)
        return {
            's1_total': s1_total,
            'number': number
        }

    def before_next_page(self):
        if self.player.bnt1 == '30 out of 50 throws':
            self.player.bnt_score += 1

        self.player.dt_bnt1 = (self.player.dt_end - self.player.dt_start) / 1000


class BNT2page(Page):
    form_model = models.Player
    form_fields = ['bnt2', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = BNT_seq.index(BNT2page) + 1 + len(CRT_seq)
        return {
            's1_total': s1_total,
            'number': number
        }

    def before_next_page(self):
        if self.player.bnt2 == '25 %':
            self.player.bnt_score += 1

        self.player.dt_bnt2 = (self.player.dt_end - self.player.dt_start) / 1000

class BNT3page(Page):
    form_model = models.Player
    form_fields = ['bnt3', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = BNT_seq.index(BNT3page) + 1 + len(CRT_seq)
        return {
            's1_total': s1_total,
            'number': number
        }

    def before_next_page(self):
        if self.player.bnt3 == '20 out of 70 throws':
            self.player.bnt_score += 1

        self.player.dt_bnt3 = (self.player.dt_end - self.player.dt_start) / 1000

class BNT4page(Page):
    form_model = models.Player
    form_fields = ['bnt4', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = BNT_seq.index(BNT4page) + 1 + len(CRT_seq)
        return {
            's1_total': s1_total,
            'number': number
        }

    def before_next_page(self):
        if self.player.bnt4 == '50 %':
            self.player.bnt_score += 1

        self.player.dt_bnt4 = (self.player.dt_end - self.player.dt_start) / 1000

""" NFC and FI """
class REIpage(Page):
    form_model = models.Player
    form_fields = ['dt_start', 'dt_end', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12', 'q13', 'q14', 'q15', 'q16', 'q17', 'q18', 'q19', 'q20', 'q21', 'q22', 'q23', 'q24', 'q25', 'q26', 'q27', 'q28', 'q29', 'q30', 'q31']#, 'q32', 'q33', 'q34', 'q35', 'q36', 'q37', 'q38', 'q39', 'q40']
    # the below are only for NFCFI31

    def before_next_page(self):
        self.player.nfcscore = (6-self.player.q1) + (6-self.player.q2) + self.player.q3 + (6-self.player.q4) + (6-self.player.q5) + (6-self.player.q6) + (6-self.player.q7) + self.player.q8 + (6-self.player.q9) + (6-self.player.q10) + (6-self.player.q11) + self.player.q12 + (6-self.player.q13) + self.player.q14 + (6-self.player.q15) + (6-self.player.q16) + self.player.q17 + (6-self.player.q18) + (6-self.player.q19)

        self.player.fiscore = self.player.q20 + self.player.q21 + self.player.q22 + self.player.q23 + self.player.q24 + self.player.q25 + self.player.q26 + self.player.q27 + self.player.q28 + self.player.q29 + self.player.q30 + self.player.q31

        self.player.dt_rei = (self.player.dt_end - self.player.dt_start) / 1000

class End(Page):
    pass


# t = 1000 * time.time() # current time in milliseconds
# np.random.seed(int(t) % 2**32)

CRT_seq = [CRT1page, CRT2page, CRT3page, CRT4page, CRT5page, CRT6page, CRT7page]

BNT_seq = [BNT1page, BNT2page, BNT3page, BNT4page]

# np.random.shuffle(CRT_seq)
# np.random.shuffle(BNT_seq)

s1_total = len(CRT_seq) + len(BNT_seq)

# page_sequence = [Introduction] + [REIpage] + CRT_seq + BNT_seq + [End]

page_sequence = [
Consent,
Introduction,
REIpage,
CRT1page,
CRT2page,
CRT3page,
CRT4page,
CRT5page,
CRT6page,
CRT7page,
BNT1page,
BNT2page,
BNT3page,
BNT4page,
End
]
