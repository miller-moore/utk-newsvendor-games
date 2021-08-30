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
Your app description
"""

def practice_generator(treatment):

    rewards = [12.3, 19.7, 8.55, 6.35, 16.6, 23.4]
    risks = [82, 58, 82, 41, 58, 41]
    certainty = [6.85, 15.67, 5.79, 1.36, 7.44, 14.11]
    display = [0, 1, 1, 1, 0, 1]

    if treatment == 'E':
        for i in range(len(rewards)):
            rewards[i] = round(rewards[i])

        for i in range(len(risks)):
            risks[i] = round(risks[i] / 10) * 10

        for i in range(len(certainty)):
            certainty[i] = round(certainty[i], 1)

    trial_list = []
    for i in range(len(rewards)):
        dum = [rewards[i], risks[i], certainty[i], display[i]]
        trial_list.append(dum)

    trial_table = pd.DataFrame(trial_list)

    columns = ['reward', 'risk', 'certainty', 'display']
    trial_table.columns = columns

    # np.random.seed(520)
    # trial_table = trial_table.sample(frac=1).reset_index(drop=True)

    return trial_table

def set_time():

    time_now = timer()

    return time_now


class Constants(BaseConstants):
    name_in_url = 'choice_practice'
    players_per_group = None
    num_rounds = 6 #should be 6


class Subsession(BaseSubsession):
    pass


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

    lottery = models.IntegerField()
