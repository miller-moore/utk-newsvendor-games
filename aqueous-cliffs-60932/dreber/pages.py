from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants, set_time


class Introduction(Page):

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        p1 = self.group.get_player_by_id(1)
        maxround = p1.participant.vars['maxround']
        return {
            'maxround': maxround
        }


class PreDecision(Page):

    def is_displayed(self):
        p1 = self.group.get_player_by_id(1)
        maxround = p1.participant.vars['maxround']
        return self.subsession.round_number <= maxround

    timeout_seconds = 2

    def vars_for_template(self):
        return {
            'roundnumber': self.round_number,
        }

    def before_next_page(self):
        self.player.starttime = set_time()


class Decision(Page):

    def is_displayed(self):
        p1 = self.group.get_player_by_id(1)
        maxround = p1.participant.vars['maxround']
        return self.subsession.round_number <= maxround

    form_model = models.Player
    form_fields = ['decision']

    def vars_for_template(self):
        prevdecision = 0
        prevothdecision = 0
        if self.round_number > 1:
            prevdecision = self.player.in_round(self.round_number - 1).decision
            prevothdecision = self.player.in_round(self.round_number - 1).other_player().decision
        return {
            'isfirstround': self.round_number == 1,
            'prevdecision': prevdecision,
            'prevothdecision': prevothdecision,
            'roundnumber': self.round_number
        }

    def before_next_page(self):
        self.player.endtime = set_time()


class ResultsWaitPage(WaitPage):

    def is_displayed(self):
        p1 = self.group.get_player_by_id(1)
        maxround = p1.participant.vars['maxround']
        return self.subsession.round_number <= maxround

    def after_all_players_arrive(self):
        for p in self.group.get_players():
            p.set_payoff()


class Results(Page):

    def is_displayed(self):
        p1 = self.group.get_player_by_id(1)
        maxround = p1.participant.vars['maxround']
        return self.subsession.round_number <= maxround

    form_model = models.Player
    form_fields = ['conflict']

    def vars_for_template(self):
        return {
            'my_decision': self.player.decision.upper(),
            'other_player_decision': self.player.other_player().decision.upper(),
            'same_choice': self.player.decision == self.player.other_player().decision,
            'earned': self.player.payoffi >= 0,
            'othearned': self.player.othpayoff >= 0,
            'lostpayoff': abs(self.player.payoffi),
            'lostothpayoff': abs(self.player.othpayoff),
            'roundnumber': self.round_number
        }


page_sequence = [
    Introduction,
    PreDecision,
    Decision,
    ResultsWaitPage,
    Results
]
