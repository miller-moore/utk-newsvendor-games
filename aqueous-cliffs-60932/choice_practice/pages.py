from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, practice_generator, set_time
import numpy as np
import pandas as pd

# This page is to be shown at the beginning of the practice session.
class Instructions(Page):

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):

        # endowment = self.session.vars['endowment']
        # pound = endowment / self.session.vars['exchange']

        endowment = 25 # set for convenience during the development
        pound = endowment / 5

        if pound.is_integer():
            pound = int(pound)

        reward = 12
        risk = 75
        certainty = 7.6

        risk_up = str(100 - risk)
        risk_up_px = ((100 - risk) / 100) * 300
        risk_down = str(risk)
        risk_down_px = (risk / 100) * 300

        win = endowment - certainty + reward
        loss = endowment - certainty

        return {
            'endowment': '$' + str(endowment),
            'pound': '£' + str(pound),

            'reward': '$' + str(reward),
            'certainty': '$' + str(certainty),

            'risk_up': risk_up,
            'risk_up_px': str(risk_up_px)+"px",
            'risk_down': risk_down,
            'risk_down_px': str(risk_down_px)+"px",

            'risk_up_posi': str(risk_up_px * 0.5 - 20)+"px",
            'risk_down_posi': str(risk_down_px * 0.5 - 20)+"px",

            'win': '$' + str(win),
            'loss': '$' + str(loss),
        }

class FixationPage(Page):

    # timer can be hidden from the page with CSS: https://otree.readthedocs.io/en/latest/timeouts.html#customizing-the-timer
    timeout_seconds = 1

    def before_next_page(self):
        self.player.pydectime = set_time() # here we set the start of the dectime in unix seconds

class DecisionPage(Page):

    form_model = 'player'
    form_fields = ['choice', 'jsdectime_start', 'jsdectime_end']

    def vars_for_template(self):

        # this determines the height of the blue and red boxes in the right stimulus
        # and the text inside them
        # can be programmed to change in every round using self.round_number in for-loop

        treatment = self.participant.vars['treatment']
        # treatment = np.random.choice(['A','E'])
        # treatment = 'A'
        # treatment = 'E'

        practice_table = practice_generator(treatment)

        reward = practice_table['reward'][self.round_number - 1]
        risk = practice_table['risk'][self.round_number - 1]
        certainty = practice_table['certainty'][self.round_number - 1]
        display = practice_table['display'][self.round_number - 1]

        if certainty.is_integer():
            certainty = int(certainty)

        self.player.reward = reward
        self.player.risk = risk
        self.player.certainty = certainty
        self.player.display = display

        risk_up = str(100 - risk)
        risk_up_px = ((100 - risk) / 100) * 300
        risk_down = str(risk)
        risk_down_px = (risk / 100) * 300

        if display == 0:
            lot_key = 'right'
            tag_key = 'left'
        else:
            lot_key = 'left'
            tag_key = 'right'

        return {
            'risk_up': risk_up,
            'risk_up_px': str(risk_up_px)+"px",
            'risk_down': risk_down,
            'risk_down_px': str(risk_down_px)+"px",

            'risk_up_posi': str(risk_up_px * 0.5 - 20)+"px",
            'risk_down_posi': str(risk_down_px * 0.5 - 20)+"px",

            'reward': '$' + str(reward),
            'certainty': '$' + str(certainty),
            'display': display,

            'lot_key':lot_key,
            'tag_key':tag_key
        }

    def before_next_page(self):
        # Python Method of dectime collection: here we subtract from current unix time the start of the decision round that was set in the fixation page
        self.player.pydectime = set_time() - self.player.pydectime

        # JavaScript Method of dectime collection:
        self.player.jsdectime = (self.player.jsdectime_end - self.player.jsdectime_start) / 1000

        self.player.treatment = self.participant.vars['treatment']

        if self.player.choice == 'right' and self.player.display == 0:
            self.player.lottery = 1
        elif self.player.choice == 'left' and self.player.display == 1:
            self.player.lottery = 1
        else:
            self.player.lottery = 0

class AfterPage(Page):
    # This AfterPage is used to display the confirmation animation, and to make the environment for Python time recording as simple as possible.

    timeout_seconds = 0.5

    def vars_for_template(self):


        reward = self.player.reward
        risk = self.player.risk
        certainty = self.player.certainty
        display = self.player.display

        choice = self.player.choice

        if reward.is_integer():
            reward = int(reward)

        if risk.is_integer():
            risk = int(risk)

        if certainty.is_integer():
            certainty = int(certainty)

        risk_up = str(100 - risk)
        risk_up_px = ((100 - risk) / 100) * 300
        risk_down = str(risk)
        risk_down_px = (risk / 100) * 300

        if display == 0:
            lot_key = 'right'
            tag_key = 'left'
        else:
            lot_key = 'left'
            tag_key = 'right'

        return {
            'risk_up': risk_up,
            'risk_up_px': str(risk_up_px)+"px",
            'risk_down': risk_down,
            'risk_down_px': str(risk_down_px)+"px",

            'risk_up_posi': str(risk_up_px * 0.5 - 20)+"px",
            'risk_down_posi': str(risk_down_px * 0.5 - 20)+"px",

            'reward': '$' + str(reward),
            'certainty': '$' + str(certainty),
            'display': display,
            'choice': choice,

            'lot_key':lot_key,
            'tag_key':tag_key
        }

    def before_next_page(self):
        if self.round_number in rest_round:
            self.player.pyresttime = set_time()
        else:
            pass


rest_limit = 300 # seconds
rest_round = [3]

class RestPage(Page):

    timeout_seconds = rest_limit
    timer_text = 'Time remaining for this break:'

    def is_displayed(self):
        # rest_after = 3
        # rest = list(range(rest_after, Constants.num_rounds, rest_after))

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
FixationPage,
DecisionPage,
AfterPage,
RestPage,
]
