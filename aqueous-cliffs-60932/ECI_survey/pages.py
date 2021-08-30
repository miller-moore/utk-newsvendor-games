from otree.api import Currency as c, currency_range
# from . import models
from ._builtin import Page, WaitPage
from .models import Constants
import numpy as np

# # The import code below does not work here becasue psycopg2 is not istalled,
# # However these codes are necessary to ensure the program to run on servers.
# from psycopg2.extensions import register_adapter, AsIs
# def addapt_numpy_float64(numpy_float64):
#     return AsIs(numpy_float64)
# def addapt_numpy_int64(numpy_int64):
#     return AsIs(numpy_int64)
# register_adapter(np.float64, addapt_numpy_float64)
# register_adapter(np.int64, addapt_numpy_int64)

class Consent(Page):
    form_model = 'player'
    form_fields = ['prolific_code']

class Introduction(Page):
    pass


class Mask(Page):
    form_model = 'player'
    form_fields = ['MU1', 'MU2', 'MU3', 'MU4', 'MU5', 'MU6',
                   'dt_start', 'dt_end']

    def before_next_page(self):
        self.player.MUF_score = self.player.MU3 + self.player.MU4 + self.player.MU5 + self.player.MU6

        self.player.dt_mask = (self.player.dt_end - self.player.dt_start) / 1000


class Remanufac(Page):
    form_model = 'player'
    form_fields = ['RM_likelytobuy', 'WTP_iPhone',
                   'RM_reliable', 'RM_fail', 'RM_returned', 'RM_problems', 'RM_cosmetic', 'RM_scratches', 'RM_worn', 'dt_start', 'dt_end']

    def before_next_page(self):

        self.player.RM_funcscore = self.player.RM_reliable + self.player.RM_fail + self.player.RM_returned + self.player.RM_problems
        self.player.RM_cosmeticscore = self.player.RM_cosmetic + self.player.RM_scratches + self.player.RM_worn
        self.player.dt_remanufac = (self.player.dt_end - self.player.dt_start) / 1000


class PANASpage(Page):
    form_model = 'player'
    form_fields = ['PA1', 'PA2', 'PA3', 'PA4', 'PA5',
                   'NA1', 'NA2', 'NA3', 'NA4', 'NA5',
                   'dt_start', 'dt_end']

    def before_next_page(self):
        self.player.PA_score = self.player.PA1 + self.player.PA2 + self.player.PA3 + \
        self.player.PA4 + self.player.PA5

        self.player.NA_score = (6 - self.player.NA1) + (6 - self.player.NA2) + \
        (6 - self.player.NA3) + (6 - self.player.NA4) + (6 - self.player.NA5)

        self.player.dt_panas = (self.player.dt_end - self.player.dt_start) / 1000


""" CRT """
class CRT1page(Page):
    # form_model = models.Player # This seems to be the old way of doing the thing but now it has changed.
    form_model = 'player'
    form_fields = ['crt1', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT1page) + 1
        return {
            'CRT_total': len(CRT_seq),
            'number': number
        }

    def before_next_page(self):
        if self.player.crt1 == '5 pence':
            self.player.reflectiveness_score += 1
        elif self.player.crt1 == '10 pence':
            self.player.intuitiveness_score += 1

        self.player.dt_crt1 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT2page(Page):
    form_model = 'player'
    form_fields = ['crt2', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT2page) + 1
        return {
            'CRT_total': len(CRT_seq),
            'number': number
        }

    def before_next_page(self):
        if self.player.crt2 == '5 minutes':
            self.player.reflectiveness_score += 1
        elif self.player.crt2 == '100 minutes':
            self.player.intuitiveness_score += 1

        self.player.dt_crt2 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT3page(Page):
    form_model = 'player'
    form_fields = ['crt3', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT3page) + 1
        return {
            'CRT_total': len(CRT_seq),
            'number': number
        }

    def before_next_page(self):
        if self.player.crt3 == '47 days':
            self.player.reflectiveness_score += 1
        elif self.player.crt3 == '24 days':
            self.player.intuitiveness_score += 1

        self.player.dt_crt3 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT4page(Page):
    form_model = 'player'
    form_fields = ['crt4', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT4page) + 1
        return {
            'CRT_total': len(CRT_seq),
            'number': number
        }

    def before_next_page(self):
        if self.player.crt4 == '4 days':
            self.player.reflectiveness_score += 1
        elif self.player.crt4 == '9 days':
            self.player.intuitiveness_score += 1

        self.player.dt_crt4 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT5page(Page):
    form_model = 'player'
    form_fields = ['crt5', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT5page) + 1
        return {
            'CRT_total': len(CRT_seq),
            'number': number
        }

    def before_next_page(self):
        if self.player.crt5 == '29 students':
            self.player.reflectiveness_score += 1
        elif self.player.crt5 == '30 students':
            self.player.intuitiveness_score += 1

        self.player.dt_crt5 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT6page(Page):
    form_model = 'player'
    form_fields = ['crt6', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT6page) + 1
        return {
            'CRT_total': len(CRT_seq),
            'number': number
        }

    def before_next_page(self):
        if self.player.crt6 == '20 pounds':
            self.player.reflectiveness_score += 1
        elif self.player.crt6 == '10 pounds':
            self.player.intuitiveness_score += 1

        self.player.dt_crt6 = (self.player.dt_end - self.player.dt_start) / 1000


class CRT7page(Page):
    form_model = 'player'
    form_fields = ['crt7', 'dt_start', 'dt_end']

    def vars_for_template(self):
        number = CRT_seq.index(CRT7page) + 1
        return {
            'CRT_total': len(CRT_seq),
            'number': number
        }

    def before_next_page(self):
        if self.player.crt7 == 'has lost money.':
            self.player.reflectiveness_score += 1
        elif self.player.crt7 == 'is ahead of where he began.':
            self.player.intuitiveness_score += 1

        self.player.dt_crt7 = (self.player.dt_end - self.player.dt_start) / 1000



class End(Page):
    pass


CRT_seq = [CRT1page, CRT2page, CRT3page, CRT4page, CRT5page, CRT6page, CRT7page]

page_sequence = [
Consent,
Introduction,
Mask,
Remanufac,
PANASpage,
CRT1page,
CRT2page,
CRT3page,
CRT4page,
CRT5page,
CRT6page,
CRT7page,
End
]


#
# page_sequence = [
# Consent,
# Introduction,
# Mask,
# Remanufac,
# PANASpage,
# CRT_seq[0],
# CRT_seq[1],
# CRT_seq[2],
# CRT_seq[3],
# CRT_seq[4],
# CRT_seq[5],
# CRT_seq[6],
# End
# ]
