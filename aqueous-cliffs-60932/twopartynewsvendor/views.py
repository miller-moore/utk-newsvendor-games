from otree.api import Currency as c, currency_range, safe_json
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, profit, custprofit, trueorderquantity, set_time
from decimal import Decimal, ROUND_HALF_UP


class WelcomePage(Page):

    def is_displayed(self):
        return self.round_number == 1

    form_model = models.Player
    form_fields = ['check1low', 'check2low', 'check3low', 'check1high', 'check2high', 'check3high', 'check4', 'check5']

    def vars_for_template(self):

        if (self.session.config['margin'] == 'low'):
            marginlow = True
            baselinereward = '0.12'

        else:
            marginlow = False
            baselinereward = '0.20'

        return {
            'baselinereward': baselinereward,
            'marginlow': marginlow,
            'margin': safe_json(self.session.config['margin']),
            'label1l': 'If your order quantity is 600 and the demand realization is 700, what is your profit?',
            'label2l': 'If your order quantity is 600, what is the probability that your profit will be 936?',
            'label3l': 'If your order quantity is 750, what is the probability that your profit will be 806?',
            'label4': 'What happens if the demand is higher than your order quantity?',
            'label5': 'If your average profit over all the rounds is 1130, what is your monetary reward from Part 2 (without the baseline reward)?',
            'label1h': 'If your order quantity is 400 and the demand realization is 500, what is your profit?',
            'label2h': 'If your order quantity is 500, what is the probability that your profit will be 700?',
            'label3h': 'If your order quantity is 800, what is the probability that your profit will be 942?',
        }


class DecideOrderQuantity(Page):

    form_model = models.Player
    form_fields = ['orderquantity']

    def vars_for_template(self):

        return {
            'round': self.player.round_number,
            'margin': safe_json(self.session.config['margin'])
        }

    def before_next_page(self):
        self.player.endtime = set_time()
        self.player.demand = self.session.vars['demand'][self.round_number - 1]
        self.player.trueorderquantity = trueorderquantity(self.player.orderquantity, self.session.config['margin'])
        self.player.payoff = profit(self.player.demand, self.player.orderquantity, self.session.config['margin'])
        self.player.custpay = custprofit(self.player.demand, self.player.orderquantity, self.session.config['margin'])


class Results(Page):

    def vars_for_template(self):

        if (self.session.config['margin'] == 'low'):
            demand = self.session.vars['demand'][self.round_number-1]
            demandindex = (demand-500)/50
        else:
            demand = self.session.vars['demand'][self.round_number - 1]
            demandindex = (demand-300)/100

        if (demandindex < self.player.orderquantity):
            demandtext = "Because demand was lower than your inventory level, you have excess units in your inventory that you could not sell to the customers."
        elif (demandindex > self.player.orderquantity):
            demandtext = "Because demand was higher than your inventory level, you could not satisfy all the customer demand."
        else:
            demandtext = "Your order quantity exactly matched demand."

        return {
            'round': self.player.round_number,
            'margin': safe_json(self.session.config['margin']),
            'orderqindex': safe_json(self.player.orderquantity),
            'demand': demand,
            'demandindex': safe_json(demandindex),
            'player_in_all_rounds': self.player.in_all_rounds(),
            'demandtext': demandtext
        }

    def before_next_page(self):
        self.player.starttime = set_time()


class FinalPage(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    form_model = models.Player
    form_fields = ['pecu','nonpecu','conflict']

    def vars_for_template(self):

        if (self.session.config['margin'] == 'low'):
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
