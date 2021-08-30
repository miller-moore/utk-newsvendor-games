from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random, time, numpy as np
from timeit import default_timer as timer

doc = """
Repeated Prisoner's Dilemma
"""


def set_time():

    timme = timer()

    return timme


class Constants(BaseConstants):

    name_in_url = 'dreber'
    players_per_group = 2

    num_rounds = 12

    instructions_template = 'prisoner/Instructions.html'

    cc = c(1)
    cdrow = c(-2)
    cdcol = c(3)
    cprow = c(-5)
    cpcol = c(1)

    dcrow = c(3)
    dccol = c(-2)
    dd = 0
    dprow = c(-3)
    dpcol = c(-2)

    pcrow = c(1)
    pccol = c(-5)
    pdrow = c(-2)
    pdcol = c(-3)
    pp = c(-5)


class Subsession(BaseSubsession):

    def creating_session(self):
        if self.round_number == 1:
            maxround = 0
            while (maxround < 1000):
                maxround += 1
                if (np.random.uniform(0, 1, 1) < 0.25): break
            for g in self.get_groups():
                p1 = g.get_player_by_id(1)
                p1.participant.vars['maxround'] = maxround


class Group(BaseGroup):

    maxround = models.PositiveIntegerField()


class Player(BasePlayer):

    decision = models.CharField(
        choices=['A', 'B', 'C'],
        doc="""This player's decision""",
        widget=widgets.RadioSelect()
    )

    payoffi = models.IntegerField()
    othpayoff = models.IntegerField()

    starttime = models.FloatField()

    endtime = models.FloatField()

    conflict = models.PositiveIntegerField(
        choices=[[1,'1'], [2,'2'], [3,'3'], [4,'4'], [5,'5'], [6,'6'], [7,'7'], [8,'8'], [9,'9']],
        widget=widgets.RadioSelectHorizontal()
    )

    def other_player(self):
        return self.get_others_in_group()[0]

    def set_payoff(self):

        points_matrix = {
            'A':
                {
                    'A': Constants.cc,
                    'B': Constants.cdrow,
                    'C': Constants.cprow
                },
            'B':
                {
                    'A': Constants.dcrow,
                    'B': Constants.dd,
                    'C': Constants.dprow
                },
            'C':
                {
                    'A': Constants.pcrow,
                    'B': Constants.pdrow,
                    'C': Constants.pp
                }
        }

        self.payoffi = int(points_matrix[self.decision][self.other_player().decision])

        self.othpayoff = int(points_matrix[self.other_player().decision][self.decision])

