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

        if self.player.qu1 == 86:
            qu1res = 'correct'
        else:
            qu1res = 'incorrect'

        if self.player.qu2 == 50:
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
        self.group.demand = set_demand()


#class ResultsWaitPage(WaitPage):
#    body_text = "Waiting for the other participant to decide."
#
#    def after_all_players_arrive(self):
#        for p in self.group.get_players():
#            p.set_payoff()


#class Results(Page):

#    def vars_for_template(self):

#        q1 = self.player.units
#        q2 = self.player.other_player().units
#        d = self.group.demand

#        if (q2 < d/2):
#            overflowd = int(round(0.8*(d/2 - q2)))
#        else:
#            overflowd = 0

#        if (q1 < d/2):
#            overflowd2 = int(round(0.8*(d/2 - q1)))
#        else:
#            overflowd2 = 0

#        if (q1 > q2):
#            efd1 = d/2 + overflowd
#            realloc = overflowd
#        else:
#            efd1 = d/2
#            realloc = 0

#        if (q2 > q1):
#            efd2 = d/2 + overflowd2
#            realloc2 = overflowd2
#        else:
#            efd2 = d/2
#            realloc2 = 0

#        revenue = 4*min(efd1,q1)
#        othrevenue = 4*min(efd2,q2)
#        cost = 2*q1
#        othcost = 2*q2

#        return {
#            'q1': q1,
#            'q2': q2,
#            'd1': int(d/2),
#            'd2': int(d/2),
#            'revenue': int(revenue),
#            'othrevenue': int(othrevenue),
#            'cost': cost,
#            'othcost': othcost,
#            'payoff': int(self.player.payoff),
#            'othpayoff': self.player.othpayoff,
#            'realloc': realloc,
#            'realloc2': realloc2,
#            'efd1': int(efd1),
#            'efd2': int(efd2)
#        }

#   def before_next_page(self):
#        self.participant.vars['part3rew'] = self.player.payoff


class Results2(Page):
    pass


class FinalPage(Page):

    def vars_for_template(self):

        rew2 = self.participant.vars['part2rew']
#        rew3 = self.participant.vars['part3rew']

#        rew = (rew2+rew3)/200

        return {
            'rew2': int(rew2),
#            'rew3': int(rew3),
#            'rew': rew,
            'prolificurl': self.session.config['prolificurl']
        }


page_sequence = [
    Introduction,
    TestQuestions,
    PreDecision,
    Decide,
#    ResultsWaitPage,
#    Results,
    FinalPage
]