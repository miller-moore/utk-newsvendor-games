from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class FirstPage(Page):
    form_model = models.Player
    form_fields = ['code']


class Instructions(Page):
    pass


class LinkPage(Page):
    form_model = models.Player
    form_fields = ['q1','q2','q3','q4','q5','q6','q7','q8','q9','q10','q11','q12','q13','q14','q15','q16','q17','q18','q19','q20','q21']


class ChoicePage1(Page):
    form_model = models.Player
    form_fields = ['q22']


class ConflictPage1(Page):
    form_model = models.Player
    form_fields = ['conflict22']

    def vars_for_template(self):

        if self.player.q22 == 1:
            choice = '(A)'
        else:
            choice = '(B)'

        return {
            'choice': choice
        }


class ChoicePage2(Page):
    form_model = models.Player
    form_fields = ['q23']


class ConflictPage2(Page):
    form_model = models.Player
    form_fields = ['conflict23']

    def vars_for_template(self):

        if self.player.q23 == 1:
            choice = '(A)'
        else:
            choice = '(B)'

        return {
            'choice': choice
        }


class ChoicePage3(Page):
    form_model = models.Player
    form_fields = ['q24']


class ConflictPage3(Page):
    form_model = models.Player
    form_fields = ['conflict24']

    def vars_for_template(self):

        if self.player.q24 == 1:
            choice = '(A)'
        else:
            choice = '(B)'

        return {
            'choice': choice
        }


class ChoicePage4(Page):
    form_model = models.Player
    form_fields = ['q25']


class ConflictPage4(Page):
    form_model = models.Player
    form_fields = ['conflict25']

    def vars_for_template(self):

        if self.player.q25 == 1:
            choice = '(A)'
        else:
            choice = '(B)'

        return {
            'choice': choice
        }


class ChoicePage5(Page):
    form_model = models.Player
    form_fields = ['q26']


class ConflictPage5(Page):
    form_model = models.Player
    form_fields = ['conflict26']

    def vars_for_template(self):

        if self.player.q26 == 1:
            choice = '(A)'
        else:
            choice = '(B)'

        return {
            'choice': choice
        }


class ChoicePage6(Page):
    form_model = models.Player
    form_fields = ['q27']


class ConflictPage6(Page):
    form_model = models.Player
    form_fields = ['conflict27']

    def vars_for_template(self):

        if self.player.q27 == 1:
            choice = '(A)'
        else:
            choice = '(B)'

        return {
            'choice': choice
        }

    def before_next_page(self):

        self.participant.vars['payoff'] = 2*(self.player.q1 + self.player.q2 + self.player.q3 + self.player.q4 + self.player.q5 + self.player.q6 + self.player.q7 + self.player.q8 + self.player.q9 + self.player.q10 + self.player.q11 + self.player.q12 + self.player.q13 + self.player.q14 + self.player.q15 + self.player.q16 + self.player.q17 + self.player.q18 + self.player.q19 + self.player.q20 + self.player.q21)


class Results(Page):
    pass


page_sequence = [
    FirstPage,
    Instructions,
    LinkPage,
    ChoicePage1,
    ConflictPage1,
    ChoicePage2,
    ConflictPage2,
    ChoicePage3,
    ConflictPage3,
    ChoicePage4,
    ConflictPage4,
    ChoicePage5,
    ConflictPage5,
    ChoicePage6,
    ConflictPage6
]

