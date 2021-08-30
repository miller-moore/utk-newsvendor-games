from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants, set_time, set_demand


class Introduction(Page):
    pass


class TestQuestions(Page):
    form_model = models.Player
    form_fields = ['qu1','qu2','qu3']


class PreDecision(Page):

    def vars_for_template(self):

        if self.player.qu1 == 90:
            qu1res = 'correct'
        else:
            qu1res = 'incorrect'

        if self.player.qu2 == 100:
            qu2res = 'correct'
        else:
            qu2res = 'incorrect'

        if self.player.qu3 == 60:
            qu3res = 'correct'
        else:
            qu3res = 'incorrect'

        return {
            'qu1': self.player.qu1,
            'qu2': self.player.qu2,
            'qu3': self.player.qu3,
            'qu1res': qu1res,
            'qu2res': qu2res,
            'qu3res': qu3res,
            'blaa': 'blaa'
        }

    def before_next_page(self):
        self.player.starttime = set_time()


class Decide(Page):
    form_model = models.Player
    form_fields = ['units']

    def before_next_page(self):
        self.player.endtime = set_time()
        self.player.demand = set_demand()
        self.player.set_payoff()


class Results(Page):

    def vars_for_template(self):

        if (self.player.units < self.player.demand):
            overflowd2 = self.player.demand - self.player.units
            revenue = 4*self.player.units
            leftovers = 0
        else:
            overflowd2 = 0
            leftovers = self.player.units - self.player.demand
            revenue = 4*self.player.demand

        cost = 2*self.player.units

        return {
            'q': self.player.units,
            'd': self.player.demand,
            'payoff': int(self.player.payoff),
            'overflowd2': overflowd2,
            'leftovers': leftovers,
            'revenue': revenue,
            'cost': cost
        }

    def before_next_page(self):
        self.participant.vars['part2rew'] = self.player.payoff


page_sequence = [
    Introduction,
    TestQuestions,
    PreDecision,
    Decide,
    Results
]
