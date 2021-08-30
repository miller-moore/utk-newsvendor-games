from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, set_time
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


class Instructions(Page):
    def is_displayed(self):
        return self.round_number == 1

class CheckPage1(Page):
    form_model = 'player'
    form_fields = ['cq1_1', 'cq1_2', 'cq1_3', 'cq1_4', 'cq1_5']

    def is_displayed(self):
        return self.round_number == 1

class CheckPage2(Page):
    form_model = 'player'
    form_fields = ['cq2_1', 'cq2_2', 'cq2_3']

    def is_displayed(self):
        return self.round_number == 1

class Pre_Practice(Page):
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

        if self.round_number == 1:
            gain = 35
            loss = 50
            display = 1

        elif self.round_number == 2:
            gain = 65
            loss = 15
            display = 1
        elif self.round_number == 3:
            gain = 75
            loss = 75
            display = 0
        elif self.round_number == 4:
            gain = 15
            loss = 60
            display = 1
        elif self.round_number == 5:
            gain = 75
            loss = 90
            display = 0
        elif self.round_number == 6:
            gain = 40
            loss = 25
            display = 0
        elif self.round_number == 7:
            gain = 15
            loss = 30
            display = 0
        elif self.round_number == 8:
            gain = 85
            loss = 50
            display = 1
        elif self.round_number == 9:
            gain = 35
            loss = 10
            display = 0
        else:
            gain = 55
            loss = 40
            display = 1

        # Recording information about the trial
        self.player.gain = gain
        self.player.loss = loss
        self.player.display = display

        return {
            'gain': "+" + str(gain),
            'loss': "–" + str(loss),
            'display': display,

            'gain_txt': gain,
            'loss_txt': loss,
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

            'accept': accept,

            'gain_txt': gain,
            'loss_txt': loss,
        }

    def before_next_page(self):
        if self.round_number in rest_round:
            self.player.pyresttime = set_time()
        else:
            pass

# Specify information about the rest page:
rest_round = [5] # a rest round in the middle
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


page_sequence = [
Instructions,
CheckPage1,
CheckPage2,
Pre_Practice,
FixationPage,
DecisionPage,
AfterPage,
RestPage
]
