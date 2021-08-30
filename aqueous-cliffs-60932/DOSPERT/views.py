from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from decimal import Decimal, ROUND_HALF_UP


class Questions(Page):
    form_model = models.Player
    form_fields = ['q1','q3','q4','q7','q8','q12','q14','q18','q21','q22','q27','q28']


class Proceed(Page):

    def vars_for_template(self):
        return {
            'prolificurl': self.session.config['prolificurl']
        }


page_sequence = [
    Questions,
    Proceed
]
