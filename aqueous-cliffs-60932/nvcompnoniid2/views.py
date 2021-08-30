from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants, set_time, set_demand, owninfo, codenotexist
import csv


class Welcome(Page):

    form_model = models.Player
    form_fields = ['prolificcode']

    def prolificcode_error_message(self, value):
        cond = codenotexist(value)
        if (cond):
            return 'The ID does not exist in our database, please check that it is given correctly (the ID should have 24 characters)'


class Introduction(Page):
    pass


class PreDecision(Page):

    def vars_for_template(self):

        owninfoo = owninfo(self.player.prolificcode)

        return {
            'ownq': owninfoo[0],
            'othq': owninfoo[1],
            'dem': owninfoo[2],
            'ownpay': owninfoo[3],
            'othpay': owninfoo[4]
        }

    def before_next_page(self):
        self.player.starttime = set_time()


class Decide(Page):
    form_model = models.Player
    form_fields = ['units']

    def vars_for_template(self):

        owninfoo = owninfo(self.player.prolificcode)

        return {
            'ownq': owninfoo[0],
            'othq': owninfoo[1],
            'dem': owninfoo[2],
            'ownpay': owninfoo[3],
            'othpay': owninfoo[4]
        }

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


#class Results2(Page):
#    pass


class FinalPage(Page):

    def vars_for_template(self):

        return {
            'prolificurl': self.session.config['prolificurl']
        }


page_sequence = [
    Welcome,
    Introduction,
    PreDecision,
    Decide,
#    ResultsWaitPage,
#    Results,
    FinalPage
]