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

        if self.player.qu1 == 66:
            qu1res = 'correct'
        else:
            qu1res = 'incorrect'

        if self.player.qu2 == 82:
            qu2res = 'correct'
        else:
            qu2res = 'incorrect'

        if self.player.qu3 == 280:
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
        }

    def before_next_page(self):
        self.player.starttime = set_time()


class Decide(Page):
    form_model = models.Player
    form_fields = ['units']

    def before_next_page(self):
        self.player.endtime = set_time()
        self.player.demand = set_demand()


#class ResultsWaitPage(WaitPage):
#    body_text = "Waiting for the other participant to decide."

#    def after_all_players_arrive(self):
#        for p in self.group.get_players():
#            p.set_payoff()


#class Results(Page):

#    def vars_for_template(self):

#        if (self.player.other_player().units < self.player.other_player().demand):
#            overflowd = self.player.other_player().demand - self.player.other_player().units
#        else:
#            overflowd = 0

#        if (self.player.units < self.player.demand):
#            overflowd2 = self.player.demand - self.player.units
#       else:
#            overflowd2 = 0

#        efd1 = self.player.demand + int(round(0.8*overflowd))
#        efd2 = self.player.other_player().demand + int(round(0.8*overflowd2))

#        revenue = 4*min(efd1,self.player.units)
#        othrevenue = 4*min(efd2,self.player.other_player().units)
#        cost = 2*self.player.units
#        othcost = 2*self.player.other_player().units

#        return {
#            'q1': self.player.units,
#            'q2': self.player.other_player().units,
#            'd1': self.player.demand,
#            'd2': self.player.other_player().demand,
#            'revenue': revenue,
#            'othrevenue': othrevenue,
#            'cost': cost,
#            'othcost': othcost,
#            'payoff': int(self.player.payoff),
#            'othpayoff': int(self.player.othpayoff),
#            'overflowd': overflowd,
#            'overflowd2': overflowd2,
#            'efd1': efd1,
#            'efd2': efd2
#        }

#    def before_next_page(self):
#        self.participant.vars['part3rew'] = self.player.payoff


class FinalPage(Page):

    pass

page_sequence = [
    Introduction,
    TestQuestions,
    PreDecision,
    Decide,
#    ResultsWaitPage,
#    Results,
    FinalPage
]