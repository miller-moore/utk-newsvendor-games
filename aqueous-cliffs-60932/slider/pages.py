from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, profit, revenue, cost, set_time


class StartPage(Page):

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):

        return {
            'margin': 'high',
            'costparam': 3 # high margin is first then low margin
        }


class PreDecision(Page):

    timeout_seconds = 0

    def before_next_page(self):
        self.player.starttime = set_time()


class DecideOrderQuantity(Page):

    form_model = 'player'
    form_fields = ['q']

    def vars_for_template(self):

        if self.player.round_number < 16: # high margin is first
            costparam = 3
            margin = 'high'

        else:
            costparam = 9
            margin = 'low'

        return {
            'round': self.player.round_number,
            'margin': margin,
            'costparam': costparam,
            'inittotalcost': 150 * costparam,
            'iswelcomepage': False
        }

    def before_next_page(self):
        if self.player.round_number < 16:
            margin = 'high'
        else:
            margin = 'low'

        self.player.d = self.session.vars['d'][self.round_number - 1]
        self.player.payoff = round(profit(self.player.d, self.player.q, margin),0)
        self.player.revenue = revenue(self.player.d, self.player.q)
        self.player.cost = cost(self.player.q, margin)
        self.player.endtime = set_time()


class Results(Page):

    def vars_for_template(self):

        if self.player.round_number < 16: # high margin is first
            costparam = 3
            margin = 'high'
        else:
            costparam = 9
            margin = 'low'

        d = self.session.vars['d'][self.round_number-1]

        if (d < self.player.q):
            demandtext = "Demand was smaller than your inventory: you have leftovers that do not bring you any profit"
        elif (d > self.player.q):
            demandtext = "Demand was larger than your inventory: you could not satisfy all the customer demand"
        else:
            demandtext = "Demand exactly matched your inventory"

        if round(self.player.payoff,0) >= 0:
            profitloss = 'You made a profit of ' + str(round(self.player.payoff,0))
        else:
            profitloss = 'You made a loss of ' + str(-round(self.player.payoff,0))

        return {
            'round': self.player.round_number,
            'margin': margin,
            'q': self.player.q,
            'd': d,
            'costi': self.player.q * costparam,
            'reve': round(self.player.payoff, 0) + self.player.q * costparam,
            'profit': round(self.player.payoff,0),
            'player_in_all_rounds': self.player.in_all_rounds(),
            'demandtext': demandtext,
            'costparam': costparam,
            'iswelcomepage': False,
            'profitloss': profitloss
        }


class FinalPage(Page):

    def is_displayed(self):
        return self.round_number == 15 or self.round_number == 30

    def vars_for_template(self):

        if self.player.round_number < 16: # high margin is first
            costparam = 3
            margin = 'high'
        else:
            costparam = 9
            margin = 'low'

        return {
            'margin': margin,
            'costparam': costparam
        }


page_sequence = [
    StartPage,
    PreDecision,
    DecideOrderQuantity,
    Results,
    FinalPage
]
