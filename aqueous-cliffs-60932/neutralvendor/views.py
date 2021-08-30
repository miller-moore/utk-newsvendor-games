from otree.api import Currency as c, currency_range, safe_json
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, profit, set_time, setdecision, setstate
from decimal import Decimal, ROUND_HALF_UP


class WelcomePage(Page):

    def is_displayed(self):
        return self.round_number == 1

    form_model = models.Player
    form_fields = ['check1', 'check2', 'check3', 'check4', 'check5']

    def vars_for_template(self):

        if (Constants.margin == 'low'):
            marginlow = True
            baselinereward = '0.12'

        else:
            marginlow = False
            baselinereward = '0.20'

        return {
            'baselinereward': baselinereward,
            'marginlow': marginlow,
            'margin': safe_json(Constants.margin),
            'label1': 'If your decision is C and the state of the world realization is S5, what is your profit?',
            'label2': 'If your decision is C, what is the probability that your profit will be 936?',
            'label3': 'If your decision is F, what is the probability that your profit will be 806?',
            'label4': 'If the state of the world is S5 in one round, what is the probability that state of world is S3 in the next round?',
            'label5': 'If your average profit over all the rounds is 1130, what is your monetary reward from Part 2 (without the baseline reward)?',
        }


class DecideOrderQuantity(Page):

    form_model = models.Player
    form_fields = ['decision']

    def vars_for_template(self):

        return {
            'round': self.player.round_number,
            'margin': safe_json(Constants.margin)
        }

    def before_next_page(self):
        self.player.endtime = set_time()
        self.player.state = int((self.session.vars['state'][self.round_number - 1]-500)/50)
        self.player.payoff = profit(self.player.state, self.player.decision)
        self.player.truedecision = setdecision(self.player.decision)
        self.player.truestate = setstate(self.player.state)


class Results(Page):

    def vars_for_template(self):

        return {
            'round': self.player.round_number,
            'margin': safe_json(Constants.margin),
            'player_in_all_rounds': self.player.in_all_rounds(),
        }

    def before_next_page(self):
        self.player.starttime = set_time()


class FinalPage(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):

        if (Constants.margin == 'low'):
            baselinereward = '0.12'

        else:
            baselinereward = '0.20'

        reward = Decimal(float(self.participant.payoff)/(1000*Constants.num_rounds)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        return {
            'averagepay': self.participant.payoff/Constants.num_rounds,
            'reward': reward,
            'baselinereward': baselinereward
        }


class PageAfterFinalPage(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):

        return {
            'prolificurl': self.session.config['prolificurl']
        }


page_sequence = [
    WelcomePage,
    DecideOrderQuantity,
    Results,
    FinalPage,
    PageAfterFinalPage,
]
