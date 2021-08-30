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

author = 'Tianqi Hu, Ilkka Leppanen'

doc = """
200 even gambles
"""

def set_time():
    time_now = timer()
    return time_now


def gamble_generator(start, end, seed):
    values = list(range(start, end + 1))

    for i in range(len(values)):
        values[i] *= 10

    gamble_list = []

    for gain in values:
        for loss in values:
            for display in range(2):
                gamble_list.append([gain, loss, display])

    columns = ['gain', 'loss', 'display']
    gamble_table = pd.DataFrame(gamble_list, columns = columns)

    np.random.seed(seed)
    gamble_table = gamble_table.sample(frac=1).reset_index(drop=True)

    return gamble_table


class Constants(BaseConstants):
    name_in_url = 'even_gamble'
    players_per_group = None
    # num_rounds = 50 # Activate this line in development
    num_rounds = 200 # Activate this line when launching the actual experiment


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
             for p in self.get_players():
                 p.participant.vars['seed2'] = np.random.randint(low = 1000, high = 10000000)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # decision time collected by JavaScript method
    jsdectime_start = models.FloatField()
    jsdectime_end = models.FloatField()
    jsdectime = models.FloatField()
    # decision time collected by Python method
    pydectime = models.FloatField()

    # Time taken during the rest round
    pyresttime = models.FloatField()

    # Information about the trial
    gain = models.FloatField()
    loss = models.FloatField()
    # display = 1: gain shown on the left
    display = models.IntegerField()

    # Whether the gamble is accepted: 1 = yes, 0 = no
    accept = models.IntegerField()

    # Payoff outcome
    pay_info = models.LongStringField()
    pay_pound = models.FloatField()


    # # To collect feedback from pilot
    # feedback_p1 = models.LongStringField(blank=True)
    # feedback_p2 = models.LongStringField(blank=True)
    # feedback_p3 = models.LongStringField(blank=True)
    # feedback_general = models.LongStringField(blank=True)
