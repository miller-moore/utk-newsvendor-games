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
import numpy as np
import pandas as pd
import re
import time

author = 'Your name here'

doc = """
Your app description
"""

def lottery_generator(scaler, min_reward, min_risk, reward_lev, risk_lev, treatment):

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

    lottery_list = []

    for reward in rewards:
        for risk in risks:
            lottery_list.append([reward, risk])

    lottery_table = pd.DataFrame(lottery_list)

    columns = ['reward', 'risk']
    lottery_table.columns = columns

    # lottery_table = lottery_table.sort_values(by=['reward'])

    return lottery_table

# The valus of these variables need to be kept same with those in the page.py
scaler = 2**0.5
min_reward = 7.85
min_risk = 41
reward_lev = 4
risk_lev = 3


def bigger(a, b):
    if a > b:
        return a
    else:
        return b

# def decimal_places(number):
#     x = re.findall(r'\.\d*', str(number))
#     places = len(x[0]) -1
#     return places


class Constants(BaseConstants):
    name_in_url = 'BDMauction'
    players_per_group = None
    num_rounds = 12
    # num_rounds should be 12 when deployed in experiment


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            # self.session.vars['endowment'] = 25 # $ assigned in one part
            # self.session.vars['exchange'] = 5 # $/£
            # The above should be set in the REI test, they are put here for the convenience of testing only.

            for p in self.get_players():
                p.participant.vars['treatment'] = np.random.choice(['A','E'])
                # p.participant.vars['treatment'] = 'A'
                # p.participant.vars['treatment'] = 'E'

                # t = 1000 * time.time() # current time in milliseconds
                # p.participant.vars['seed2'] = int(t) % 2**32


class Group(BaseGroup):
    pass

class Player(BasePlayer):

    treatment = models.StringField()

    WTP = models.FloatField()

    # decision time collected by JavaScript method
    jsdectime_start = models.FloatField()
    jsdectime_end = models.FloatField()
    jsdectime = models.FloatField()

    reward = models.FloatField()
    risk = models.FloatField()

    # floor = models.FloatField()

    payoff_auc = models.LongStringField()

    ### check up questions ###
    cq_l1 = models.PositiveIntegerField(
        choices = [[1,'30%'],[2, '70%'],[3, '10%'],[4, '25%']], widget=widgets.RadioSelect())

    cq_l2 = models.PositiveIntegerField(
        choices = [[1,'30%'],[2, '70%'],[3, '10%'],[4, '25%']], widget=widgets.RadioSelect())

    cq_l3 = models.PositiveIntegerField(
        choices = [[1,'$30'],[2, '$70'],[3, '$10'],[4, '$25']], widget=widgets.RadioSelect())

    cq_a1 = models.PositiveIntegerField(
        choices = [[1,'$25'],[2, '$35'],[3, '$16'],[4, 'None of the above']], widget=widgets.RadioSelect())

    cq_a2 = models.PositiveIntegerField(
        choices = [[1,'$19'],[2, '$29'],[3, '$31'],[4, '$21']], widget=widgets.RadioSelect())

    cq_a3 = models.PositiveIntegerField(
        choices = [[1,'$19'],[2, '$29'],[3, '$31'],[4, '$21']], widget=widgets.RadioSelect())


    def cq_l1_error_message(self, value):
        if value != 2:
            return "Your answer to the question 1 is wrong. The number written inside the blue box represents the probability of winning the lottery"

    def cq_l2_error_message(self, value):
        if value != 1:
            return "Your answer to the question 2 is wrong. The number written inside the red box represents the probability of losing the lottery"

    def cq_l3_error_message(self, value):
        if value != 3:
            return "Your answer to the question 3 is wrong. The reward of winning the lottery is represented by the monetary amount at the bottom."

    def cq_a1_error_message(self, value):
        if value != 1:
            return "Your answer to the question 1 is wrong. If the random selling price is greater than your bid price, you would not purchase the lottery and keep the entire $25, which is the fund assigned to you at the beginning."

    def cq_a2_error_message(self, value):
        if value != 3:
            return "Your answer to the question 2 is wrong. If the random selling price is less than or equal to your bid price, you would purchase the lottery. In case you win the lottery, your payment increases to the assigned fund minus the selling price plus the lottery reward (assigned fund - selling price + lottery reward)."

    def cq_a3_error_message(self, value):
        if value != 4:
            return "Your answer to the question 3 is wrong. If the random selling price is less than or equal to your bid price, you would purchase the lottery. In case you lose the lottery, your payment drops to the assigned fund minus the selling price (assigned fund - selling price)."


    def WTP_error_message(self, value):

        treatment = self.participant.vars['treatment']
        # treatment = random.choice(['A','E'])
        # treatment = 'A'
        # treatment = 'E'

        lottery_table = lottery_generator(scaler, min_reward, min_risk, reward_lev, risk_lev, treatment)

        # ceiling = lottery_table['reward'][self.round_number - 1]

        reward = lottery_table['reward'][self.round_number - 1]
        # risk = lottery_table['risk'][self.round_number - 1]

        if self.round_number == 1:
            floor = 0
        elif reward == min_reward or reward == round(min_reward):
            floor = self.in_round(self.round_number - 1).WTP
        elif self.round_number % risk_lev == 1:
            floor = self.in_round(self.round_number - risk_lev).WTP
        else:
            floor = bigger(self.in_round(self.round_number - 1).WTP, self.in_round(self.round_number - risk_lev).WTP)


        if value >= reward:
             return "your bid price is above the reasonable price range."

        if value <= floor:
             return "your bid price is below the reasonable price range."

        # if decimal_places(value) > 2:
        #     return "your specified price cannot have a unit smaller than $0.01."



    # def WTP_max(self):
    #
    #     # ceiling = self.reward
    #
    #     treatment = self.participant.vars['treatment']
    #     # treatment = random.choice(['A','E'])
    #     # treatment = 'A'
    #     # treatment = 'E'
    #
    #     lottery_table = lottery_generator(scaler, min_reward, min_risk, reward_lev, risk_lev, treatment)
    #
    #     ceiling = lottery_table['reward'][self.round_number - 1]
    #
    #     return ceiling
    #
    # def WTP_min(self):
    #
    #     treatment = self.participant.vars['treatment']
    #     # treatment = random.choice(['A','E'])
    #     # treatment = 'A'
    #     # treatment = 'E'
    #
    #     lottery_table = lottery_generator(scaler, min_reward, min_risk, reward_lev, risk_lev, treatment)
    #
    #     reward = lottery_table['reward'][self.round_number - 1]
    #     # risk = lottery_table['risk'][self.round_number - 1]
    #
    #     if self.round_number == 1:
    #         floor = 0
    #         return floor
    #     elif reward == min_reward or reward == round(min_reward):
    #         floor = self.in_round(self.round_number - 1).WTP
    #         return floor
    #     elif self.round_number % risk_lev == 1:
    #         floor = self.in_round(self.round_number - risk_lev).WTP
    #         return floor
    #     else:
    #         floor = bigger(self.in_round(self.round_number - 1).WTP, self.in_round(self.round_number - risk_lev).WTP)
    #         return floor
    #
