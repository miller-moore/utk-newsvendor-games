from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
from timeit import default_timer as timer

import numpy as np
import pandas as pd
import time

author = 'Your name here'

doc = """
App with decision task, to come after elicitation task
"""

def trial_generator(scaler, min_reward, min_risk, reward_lev, risk_lev, m_values, treatment):

    rewards = []
    risks = []

    counter = 1
    if treatment == 'A':
        while counter <= reward_lev:
            rewards.append(min_reward)
            min_reward *= scaler
            min_reward = round(min_reward, 2)
            counter += 1
    else:
        while counter <= reward_lev:
            rewards.append(round(min_reward))
            min_reward *= scaler
            min_reward = round(min_reward, 2)
            counter += 1

    counter = 1
    if treatment == 'A':
        while counter <= risk_lev:
            risks.append(min_risk)
            min_risk *= scaler
            min_risk = round(min_risk)
            counter += 1
    else:
        while counter <= risk_lev:
            risks.append(round(min_risk / 10) * 10)
            min_risk *= scaler
            min_risk = round(min_risk)
            counter += 1

    trial_list = []
    for reward in rewards:
        for risk in risks:
            for m in m_values:
                if risk < 50:
                    devider = (2 ** 1.5) ** (m / 4)
                elif risk < 70:
                    devider = 2 ** (m / 4)
                else:
                    devider = (2 ** 0.5) ** (m / 4)

                if treatment == 'A':
                    certainty = round(reward / devider, 2)
                else:
                    certainty = round(reward / devider, 1)

                for display in range(2):
                    trial_list.append([reward, risk, certainty, display])

    trial_table = pd.DataFrame(trial_list)

    columns = ['reward', 'risk', 'certainty', 'display']
    trial_table.columns = columns

    np.random.seed(520)
    trial_table = trial_table.sample(frac=1).reset_index(drop=True)

    return trial_table


def set_time():

    time_now = timer()

    return time_now


class Constants(BaseConstants):
    name_in_url = 'cognitivenoise'
    players_per_group = None
    num_rounds = 12
    # num_rounds = 216
    # num_rounds should be changed to 216 when deployed in experiment, also to change the rest_round in the page file.

    # instructions_template = 'cognitivenoise/Instructions.html'
    # In a template: "You can write the instructions on a template file and include here using the below line: {% include Constants.instructions_template %}"


class Subsession(BaseSubsession):
    pass

    # def creating_session(self):
    #     if self.round_number == 1:
    #          for p in self.get_players():
    #              t = 1000 * time.time() # current time in milliseconds
    #              p.participant.vars['seed3'] = int(t) % 2**32

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.StringField()

    choice = models.StringField()

    # decision time collected by JavaScript method
    jsdectime_start = models.FloatField()
    jsdectime_end = models.FloatField()
    jsdectime = models.FloatField()
    # decision time collected by Python method
    pydectime = models.FloatField()

    pyresttime = models.FloatField()

    reward = models.FloatField()
    risk = models.FloatField()
    certainty = models.FloatField()
    display = models.IntegerField()

    # Whether the lottery is chosen in the trial: 1 = yes, 0 = no
    lottery = models.IntegerField()

    decmode = models.PositiveIntegerField(
        choices = [
        [7, 'Almost always (near 100% of the time)'],
        [6, 'Very often (about 80% of the time)'],
        [5, 'Moderately often (about 60% of the time)'],
        [4, 'About half of the time (50% of the time)'],
        [3, 'Moderately seldom (about 40% of the time)'],
        [2, 'Very seldom (about 20% of the time)'],
        [1, 'Almost never (near 0% of the time)'],
        ],
        widget=widgets.RadioSelect())

    payoff_ddm = models.LongStringField()
    pay_pound = models.FloatField()

    # To collect feedback from pilot

    # feedback_p1 = models.LongStringField(blank=True)
    # feedback_p2 = models.LongStringField(blank=True)
    # feedback_p3 = models.LongStringField(blank=True)
    # feedback_general = models.LongStringField(blank=True)
