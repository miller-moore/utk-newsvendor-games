from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from decimal import Decimal, ROUND_HALF_UP


class Questions(Page):
    form_model = models.Player
    form_fields = ['q1','q2','q3','q4','q5','q6','q7','q8','q9','q10']

    #def before_next_page(self):
    #    self.player.erqscore = self.player.q1


class Proceed(Page):

    def vars_for_template(self):

        return {

        }


page_sequence = [
    Questions,
    Proceed
]
