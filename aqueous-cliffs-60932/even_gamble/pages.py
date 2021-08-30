from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, set_time, gamble_generator
import numpy as np
import pandas as pd
import time

# # The import code below does not work here becasue psycopg2 is not istalled,
# # However these codes are necessary to ensure the program to run on servers.
from psycopg2.extensions import register_adapter, AsIs
def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)
register_adapter(np.float64, addapt_numpy_float64)
register_adapter(np.int64, addapt_numpy_int64)


class InitialPage(Page):
    def is_displayed(self):
        return self.round_number == 1

class FixationPage(Page):
    # timeout_seconds = 0.5
    # This page should stay for 1 second in real experiment

    timeout_seconds = 1

    def before_next_page(self):
        self.player.pydectime = set_time() # here we set the start of the dectime in unix seconds


class DecisionPage(Page):

    form_model = 'player'
    form_fields = ['accept', 'jsdectime_start', 'jsdectime_end']

    def vars_for_template(self):

        # In the actual experiment, start = 1 and end = 10
        start = 1
        end = 10
        # seed = 666888
        seed = self.participant.vars['seed2']

        trial_table =  gamble_generator(start = start, end = end, seed = seed)

        gain = int(trial_table['gain'][self.round_number - 1])
        loss = int(trial_table['loss'][self.round_number - 1])
        display = trial_table['display'][self.round_number - 1]

        # Recording information about the trial
        self.player.gain = gain
        self.player.loss = loss
        self.player.display = display

        return {
            'gain': "+" + str(gain),
            'loss': "–" + str(loss),
            'display': display,
        }

    def before_next_page(self):
        # Python Method of dectime collection:
        self.player.pydectime = set_time() - self.player.pydectime
        # JavaScript Method of dectime collection:
        self.player.jsdectime = (self.player.jsdectime_end - self.player.jsdectime_start) / 1000


class AfterPage(Page):
    # This AfterPage is used to display the confirmation animation, and to make the environment for Python time recording as simple as possible.

    timeout_seconds = 0.5

    def vars_for_template(self):

        # reading the information about the current trial
        gain = int(self.player.gain)
        loss = int(self.player.loss)
        display = self.player.display

        accept = self.player.accept

        return {
            'gain': "+" + str(gain),
            'loss': "–" + str(loss),
            'display': display,

            'accept': accept
        }

    def before_next_page(self):
        if self.round_number in rest_round:
            self.player.pyresttime = set_time()
        else:
            pass

# Specify information about the rest page:
# rest_round = [25] # for testing during development
rest_round = [50, 100, 150] # In actual experiment rest after trial 50, 100 and 150

rest_limit = 300 # seconds

class RestPage(Page):
    timeout_seconds = rest_limit
    timer_text = 'Time remaining for this break:'

    def is_displayed(self):
        rest = rest_round

        if self.round_number in rest:
            return True
        else:
            return False

    def vars_for_template(self):
        rest_minites = rest_limit / 60

        if rest_minites.is_integer():
            rest_minites = int(rest_minites)

        trials_gone = self.round_number
        trials_left = Constants.num_rounds - self.round_number

        return {
            'rest_minites': rest_minites,

            'trials_gone': trials_gone,
            'trials_left': trials_left
        }

    def before_next_page(self):
        self.player.pyresttime = set_time() - self.player.pyresttime


class FinishPage(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):

        # Otherwise a participant can refresh the page to get desired outcome
        seed = self.participant.vars['seed2']
        np.random.seed(seed)

        # initial fund and exchange rate
        endowment = 100 # 100 experiment points given at the beginning
        exchange = 20 # 20 points = 1£

        # pick a round to count for the final payment:
        pick_round = np.random.choice(range(1, Constants.num_rounds +1))

        gain = int(self.player.in_round(pick_round).gain)
        loss = int(self.player.in_round(pick_round).loss)

        win = np.random.randint(2) # 0 or 1

        # payment if the gamble is accepted
        if win == True:
            pay_point = endowment + gain
            pay_pound = round(pay_point / exchange, 2)
        else:
            pay_point = endowment - loss
            pay_pound = round(pay_point / exchange, 2)

        # payment if the gamble is rejected
        accept = self.player.in_round(pick_round).accept
        if not accept:
            pay_point = endowment
            pay_pound = round(endowment / exchange,2)

        # record all the information about the picked trial
        pay_info = {"endowment": endowment, "exchange": exchange, "pick_round": pick_round, "gain": gain, "loss": loss, "accept": accept, "win": win, "pay_point": pay_point, "pay_pound": pay_pound}

        # record the payoff info
        self.player.pay_info = str(pay_info)
        self.player.pay_pound = pay_pound

        # for display, make pay_pound an integer if it is an interger
        if pay_pound.is_integer():
            pay_pound = int(pay_pound)

        # scenario verdict
        if accept == False:
            scenario = 1
            # the gamble is rejected

        if accept == True and win == False:
            scenario = 2
            # accept and lose the gamble

        if accept == True and win == True:
            scenario = 3
            # accept and win the gamble

        return {

            'scenario': scenario,

            'endowment': endowment,
            'pick_round': pick_round,

            'gain': gain,
            'loss': loss,
            'accept': accept,

            'pay_point': pay_point,
            'pay_pound': pay_pound,

            'prolificurl': self.session.config['prolificurl']
            # 'prolificurl': 'http://www.google.com'
        }

# class FeedbackPage(Page):
#
#     form_model = 'player'
#     form_fields = ['feedback_p1', 'feedback_p2', 'feedback_p3', 'feedback_general']
#
#     def is_displayed(self):
#         return self.round_number == Constants.num_rounds


page_sequence = [
InitialPage,
FixationPage,
DecisionPage,
AfterPage,
RestPage,
FinishPage
]
