from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, set_time


class FixationPage(Page):

    timeout_seconds = 0.5

    def before_next_page(self):
        self.player.dectime = set_time() # here we set the start of the dectime in unix seconds


class MyPage(Page):

    form_model = 'player'
    form_fields = ['choice','jsdectime_start','jsdectime_end']

    def before_next_page(self):
        self.player.dectime = set_time() - self.player.dectime # here we subtract from current unix time the start of the decision round that was set in the fixation page
        self.player.afterpage_time = set_time()

class AfterPage(Page):

    timeout_seconds = 0.5

    def vars_for_template(self):
        jsdectime = self.player.jsdectime_end - self.player.jsdectime_start

        choice = self.player.choice

        return {
            'choice': choice,
            'jsdectime': jsdectime
        }

    def before_next_page(self):
        self.player.afterpage_time = set_time() - self.player.afterpage_time # this is used only for testing, not in final app


page_sequence = [FixationPage, MyPage, AfterPage]
