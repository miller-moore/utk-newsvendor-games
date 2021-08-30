from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, set_time, trial_generator
import numpy as np
import pandas as pd
import time

class InitialPage(Page):

    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):

        t = 1000 * time.time() # current time in milliseconds
        self.participant.vars['seed3'] = int(t) % 2**32

class FixationPage(Page):

    # timeout_seconds = 0.5
    # This page should stay for 1 second in real experiment

    timeout_seconds = 1

    def before_next_page(self):
        self.player.pydectime = set_time() # here we set the start of the dectime in unix seconds


class DecisionPage(Page):

    # timeout_seconds = 2

    form_model = 'player'
    form_fields = ['choice', 'jsdectime_start', 'jsdectime_end']

    def vars_for_template(self):

        # this determines the height of the blue and red boxes in the right stimulus
        # and the text inside them
        # can be programmed to change in every round using self.round_number in for-loop

        # activate the line below in the actual deployment
        # treatment = self.participant.vars['treatment']
        # treatment = np.random.choice(['A','E'])
        # treatment = 'A'
        treatment = 'E'

        scaler = 2**0.5
        min_reward = 7.85
        min_risk = 41
        reward_lev = 4
        risk_lev = 3
        m_values = list(range(0,9))

        trial_table = trial_generator(scaler, min_reward, min_risk, reward_lev, risk_lev, m_values, treatment)

        reward = trial_table['reward'][self.round_number - 1]
        risk = trial_table['risk'][self.round_number - 1]
        certainty = trial_table['certainty'][self.round_number - 1]
        display = trial_table['display'][self.round_number - 1]

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
        }

    def before_next_page(self):
        # Python Method of dectime collection: here we subtract from current unix time the start of the decision round that was set in the fixation page
        self.player.pydectime = set_time() - self.player.pydectime

        # JavaScript Method of dectime collection:
        self.player.jsdectime = (self.player.jsdectime_end - self.player.jsdectime_start) / 1000

        # activate the line below in the actual deployment
        # self.player.treatment = self.participant.vars["treatment"]

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
            'choice': choice
        }

    def before_next_page(self):
        if self.round_number in rest_round:
            self.player.pyresttime = set_time()
        else:
            pass

rest_limit = 300 # seconds

# rest_round = [5]
rest_round = [72, 144]
# In actual experiment rest after trial 72 and 144

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


class FinalSurvey(Page):

    form_model = 'player'
    form_fields = ['decmode']

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


class FinishPage(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):

        # Otherwise a participant can refresh the page to get desired outcome
        seed = self.participant.vars['seed3']
        np.random.seed(seed)

        ######
        payoff_auc = self.participant.vars['payoff_auc']

        ######
        endowment = self.session.vars['endowment']
        exchange = self.session.vars['exchange']
        # endowment = 25
        # exchange = 5

        pick_round = np.random.choice(range(1, Constants.num_rounds +1))

        reward = self.player.in_round(pick_round).reward
        risk = int(self.player.in_round(pick_round).risk)
        certainty = self.player.in_round(pick_round).certainty
        display = self.player.in_round(pick_round).display
        lottery = self.player.in_round(pick_round).lottery

        if lottery == 1:
            # lottery is chosen
            proceed = True
        else:
            proceed = False

        dice = np.random.randint(1, 101)
        if dice <= risk:
            win = True
            payoff = round(endowment - certainty + reward, 2)
        else:
            win = False
            payoff = round(endowment - certainty, 2)

        payoff_ddm = {"endowment": endowment, "pick_round": pick_round, "reward": reward, "risk": risk, "certainty": certainty, "proceed": proceed, "win": win, "payoff": payoff}

        # record the payoff info
        self.player.payoff_ddm = str(payoff_ddm)

        pay_sum = payoff_auc['payoff'] + payoff_ddm['payoff']
        pay_pound = round(pay_sum / exchange, 2)
        self.player.pay_pound = pay_pound

        # scenario verdict
        if payoff_auc["proceed"] == False:
            scenario_auc = 1
            # In auction: no lottery

        if payoff_auc["proceed"] == True and payoff_auc["win"] == False:
            scenario_auc = 2
            # In auction: lose lottery

        if payoff_auc["proceed"] == True and payoff_auc["win"] == True:
            scenario_auc = 3
            # In auction: win lottery

        if payoff_ddm["proceed"] == False:
            scenario_ddm = 1
            # In choice: no lottery

        if payoff_ddm["proceed"] == True and payoff_ddm["win"] == False:
            scenario_ddm = 2
            # In choice: lose lottery

        if payoff_ddm["proceed"] == True and payoff_ddm["win"] == True:
            scenario_ddm = 3
            # In choice: win lottery


        if scenario_auc == 1 and scenario_ddm == 1:
            pay_sum = payoff_auc['endowment'] + payoff_ddm['endowment']
        elif scenario_auc == 1 and scenario_ddm != 1:
            pay_sum = payoff_auc['endowment'] + payoff_ddm['payoff']
        elif scenario_auc != 1 and scenario_ddm == 1:
            pay_sum = payoff_auc['payoff'] + payoff_ddm['endowment']
        else:
            pay_sum = payoff_auc['payoff'] + payoff_ddm['payoff']

        pay_sum = round(pay_sum, 2)
        pay_pound = round(pay_sum / exchange, 2)
        self.player.pay_pound = pay_pound

        return {
            'scenario_auc': scenario_auc,
            'scenario_ddm': scenario_ddm,

            'endowment_auc': payoff_auc["endowment"],
            'pick_round_auc': payoff_auc["pick_round"],
            'reward_auc': payoff_auc["reward"],
            'risk_auc': payoff_auc["risk"],
            'WTP_auc': payoff_auc["WTP"],
            'selling_price_auc': payoff_auc["selling_price"],
            'payoff_auc': payoff_auc["payoff"],

            'endowment_ddm': payoff_ddm["endowment"],
            'pick_round_ddm': payoff_ddm["pick_round"],
            'reward_ddm': payoff_ddm["reward"],
            'risk_ddm': payoff_ddm["risk"],
            'certainty_ddm': payoff_ddm["certainty"],
            'payoff_ddm': payoff_ddm["payoff"],

            'pay_sum': pay_sum,
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
FinalSurvey,
FinishPage,
]
