from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from decimal import Decimal, ROUND_HALF_UP


class firstpage(Page):
    form_model = models.Player
    form_fields = ['name', 'email', 'student_number']


class allportpage(Page):
    form_model = models.Player
    form_fields = ['q1a', 'q1b','q2a', 'q2b','q3a', 'q3b','q4a', 'q4b', 'q5a', 'q5b','q6a', 'q6b','q7a', 'q7b','q8a', 'q8b','q9a', 'q9b','q10a', 'q10b','q11a', 'q11b','q12a', 'q12b','q13a', 'q13b','q14a', 'q14b','q15a', 'q15b','q16a', 'q16b','q17a', 'q17b','q18a', 'q18b','q19a', 'q19b','q20a', 'q20b','q21a', 'q21b','q22a', 'q22b','q23a', 'q23b','q24a', 'q24b','q25a', 'q25b','q26a', 'q26b','q27a', 'q27b','q28a', 'q28b','q29a', 'q29b','q30a', 'q30b','qq1a', 'qq1b', 'qq1c', 'qq1d','qq2a', 'qq2b', 'qq2c', 'qq2d','qq3a', 'qq3b', 'qq3c', 'qq3d','qq4a', 'qq4b', 'qq4c', 'qq4d','qq5a', 'qq5b', 'qq5c', 'qq5d','qq6a', 'qq6b', 'qq6c', 'qq6d','qq7a', 'qq7b', 'qq7c', 'qq7d','qq8a', 'qq8b', 'qq8c', 'qq8d','qq9a', 'qq9b', 'qq9c', 'qq9d','qq10a', 'qq10b', 'qq10c', 'qq10d','qq11a', 'qq11b', 'qq11c', 'qq11d','qq12a', 'qq12b', 'qq12c', 'qq12d','qq13a', 'qq13b', 'qq13c', 'qq13d','qq14a', 'qq14b', 'qq14c', 'qq14d','qq15a', 'qq15b', 'qq15c', 'qq15d']

    def before_next_page(self):
        self.player.allportth = self.player.q1a + self.player.q3a + self.player.q6a + self.player.q10b + self.player.q12b + self.player.q15b + self.player.q18a + self.player.q21b + self.player.q25b + self.player.q28a + self.player.qq2a + self.player.qq3c + self.player.qq5c + self.player.qq6d + self.player.qq7a + self.player.qq9b + self.player.qq10a + self.player.qq11b + self.player.qq13d + self.player.qq15c
        self.player.allportec = self.player.q1b + self.player.q4a + self.player.q7a + self.player.q11b + self.player.q15a + self.player.q20a + self.player.q22a + self.player.q24b + self.player.q26a + self.player.q29a + self.player.qq1b + self.player.qq3d + self.player.qq4a + self.player.qq5a + self.player.qq7b + self.player.qq8d + self.player.qq10d + self.player.qq12c + self.player.qq13c + self.player.qq15b
        self.player.allportae = self.player.q2a + self.player.q5a + self.player.q8a + self.player.q10a + self.player.q13b + self.player.q16b + self.player.q18b + self.player.q22b + self.player.q27b + self.player.q29b + self.player.qq2c + self.player.qq3a + self.player.qq4d + self.player.qq6b + self.player.qq8a + self.player.qq9c + self.player.qq10b + self.player.qq12b + self.player.qq14d + self.player.qq15d
        self.player.allportso = self.player.q3b + self.player.q5b + self.player.q7b + self.player.q9b + self.player.q14b + self.player.q17a + self.player.q20b + self.player.q23a + self.player.q25a + self.player.q27a + self.player.qq1a + self.player.qq3b + self.player.qq5d + self.player.qq6c + self.player.qq8b + self.player.qq9d + self.player.qq11c + self.player.qq12d + self.player.qq13a + self.player.qq14b
        self.player.allportpo = self.player.q4b + self.player.q8b + self.player.q12a + self.player.q14a + self.player.q16a + self.player.q19a + self.player.q21a + self.player.q23b + self.player.q26b + self.player.q30b + self.player.qq1d + self.player.qq2b + self.player.qq4c + self.player.qq6a + self.player.qq7d + self.player.qq8c + self.player.qq10c + self.player.qq11a + self.player.qq13b + self.player.qq14a
        self.player.allportre = self.player.q2b + self.player.q6b + self.player.q9a + self.player.q11a + self.player.q13a + self.player.q17b + self.player.q19b + self.player.q24a + self.player.q28b + self.player.q30a + self.player.qq1c + self.player.qq2d + self.player.qq4b + self.player.qq5b + self.player.qq7c + self.player.qq9a + self.player.qq11d + self.player.qq12a + self.player.qq14c + self.player.qq15a


class REIpage(Page):
    form_model = models.Player
    form_fields = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12', 'q13', 'q14', 'q15', 'q16', 'q17', 'q18', 'q19', 'q20', 'q21', 'q22', 'q23', 'q24', 'q25', 'q26', 'q27', 'q28', 'q29', 'q30', 'q31']#, 'q32', 'q33', 'q34', 'q35', 'q36', 'q37', 'q38', 'q39', 'q40']
    # the below are only for NFCFI31
    def before_next_page(self):
        self.player.nfcscore = (6-self.player.q1) + (6-self.player.q2) + self.player.q3 + (6-self.player.q4) + (6-self.player.q5) + (6-self.player.q6) + (6-self.player.q7) + self.player.q8 + (6-self.player.q9) + (6-self.player.q10) + (6-self.player.q11) + self.player.q12 + (6-self.player.q13) + self.player.q14 + (6-self.player.q15) + (6-self.player.q16) + self.player.q17 + (6-self.player.q18) + (6-self.player.q19)
        self.player.fiscore = self.player.q20 + self.player.q21 + self.player.q22 + self.player.q23 + self.player.q24 + self.player.q25 + self.player.q26 + self.player.q27 + self.player.q28 + self.player.q29 + self.player.q30 + self.player.q31


class Results(Page):

    def vars_for_template(self):

        payoff = Decimal(float(self.participant.vars['payoff'])/10).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
        total = Decimal(float(self.participant.vars['payoff'])/10 + 1.2 + 3.00).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
        nfcscore = self.player.nfcscore
        fiscore = self.player.fiscore
        allportth = self.player.allportth
        allportec = self.player.allportec
        allportpo = self.player.allportpo
        allportae = self.player.allportae
        allportso = self.player.allportso
        allportre = self.player.allportre

        return {
            'prolificurl': self.session.config['prolificurl'],
            'payoff': payoff,
            'total': total,
            'nfcscore': nfcscore,
            'fiscore': fiscore,
            'allportth': allportth,
            'allportec': allportec,
            'allportpo': allportpo,
            'allportae': allportae,
            'allportso': allportso,
            'allportre': allportre
        }


page_sequence = [
    allportpage,
    REIpage,
    Results
]
