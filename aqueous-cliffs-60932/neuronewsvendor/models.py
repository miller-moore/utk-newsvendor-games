from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random, time, csv
from timeit import default_timer as timer


author = 'IL'

doc = """
Newsvendor game with within-subject block treatments (attend, reappraise)
Payoffs given in a payoff table
High and low margin treatments
"""


def blocktitle(round, blocks):
    #blocks = self.session.config['blocks']
    if (round % 5 == 0):
        blocknumber = int((round - (round % 5)) / 5) - 1

    else:
        blocknumber = int((round - (round % 5)) / 5 + 1) - 1

    if round < 6:

        blocktitlee = 'Practice'

    else:

        if blocks[blocknumber - 1] == 'reap':
            blocktitlee = 'Reappraise'

        else:
            blocktitlee = 'Attend'

    return blocktitlee


def blockinstruction(blocktitleee):

    if blocktitleee == 'Practice':
        blockinstr = 'The next 5 rounds are practice rounds. These rounds do not count towards your final monetary rewards. After the fifth round, the proper rounds will begin.'

    elif blocktitleee == 'Reappraise':
        blockinstr = 'During the next 5 rounds, think of each inventory decision in the context of all decisions that you make during the &quot;Reappraise&quot; rounds. That is, treat each decision as one of many monetary decisions, which will eventually constitute a &quot;portfolio&quot;. Remind yourself that you are making many of these similar decisions.</p><p>Imagine you are considering one of the inventory decisions in this task right now.</p><p>One way to think of this instruction is to imagine yourself as a professional inventory manager. You constantly take risks of exceeding demand or not meeting demand, for a living. Imagine that this is your job and that the money that you use to buy items to the inventory is not yours -- it is your company&#39;s money. Of course, you still want to do well (your job depends on it). You have done this for a long time, though, and will continue to. All that matters is that you come out on top in the end -- a mismatch between inventory level and demand here or there will not matter in terms of your overall portfolio.</p><p>It is important that you focus on the decisions in the context of all of the other decisions you will be making today during the &quot;Reappraise&quot; rounds.'

    else:
        blockinstr = 'During the next 5 rounds, focus on the inventory decisions in complete isolation from all other decisions. Tell yourself that each decision round is the only round that matters. Approach each round as if you are making only this one decision in today&#39;s study.</p><p>Concentrate on the decision in that one round, the possible demand realizations, and the possible outcomes. Ask yourself how you would feel if your inventory matches the demand exactly, how you would feel if you fall short of matching the demand, and how you feel about having excess inventory due to low demand. Just let any thoughts or emotions about that particular decision occur naturally, without trying to control them.</p><p>It is important that you focus on the decision in front of you at that time, in isolation from any context.'

    return blockinstr


def trueorderquantity(orderquantity, margin):

    if (margin == 'low'):
        toq = 500 + orderquantity * 50
    else:
        toq = 300 + orderquantity * 100

    return toq


def profit(demand, orderquantity, margin):

    toq = trueorderquantity(orderquantity, margin)

    if (margin == 'low'):
        if (demand >= toq):
            prof = 7.28 * toq - 5.72 * toq
        else:
            prof = 7.28 * demand - 5.72 * toq

    else:
        if (demand >= toq):
            prof = 1.78 * toq - 0.38 * toq
        else:
            prof = 1.78 * demand - 0.38 * toq

    return prof


def set_time():

    timme = timer()

    return timme


class Constants(BaseConstants):

    name_in_url = 'neuronewsvendor'
    players_per_group = None
    num_rounds = 45 # 5 practice rounds, 4*5 attend rounds, 4*5 reappraise rounds = 45
    endowment = None


class Subsession(BaseSubsession):

    def before_session_starts(self):

        ifile = open('randomdemand.csv', 'rt')
        dema = []
        try:
            reader = csv.reader(ifile)
            for row in reader:
                dema.append(list(map(int, row)))
        finally:
            ifile.close()

        if (self.session.config['margin'] == 'low'):
            self.session.vars['demand'] = dema[0]

        else:
            self.session.vars['demand'] = dema[1]


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    starttime = models.FloatField()
    endtime = models.FloatField()
    orderquantity = models.PositiveIntegerField(choices=[0, 1, 2, 3, 4, 5, 6], widget=widgets.RadioSelect())
    trueorderquantity = models.PositiveIntegerField()
    demand = models.PositiveIntegerField()
    block = models.StringField()
    check1low = models.PositiveIntegerField(
        choices=[[1, '936'], [2, '364'], [3, '858']], widget=widgets.RadioSelect(), blank=True)
    check2low = models.PositiveIntegerField(
        choices=[[1, '0'], [2, '1/7'], [3, '5/7']], widget=widgets.RadioSelect(), blank=True)
    check3low = models.PositiveIntegerField(
        choices=[[1, '5/7'], [2, '1/7'], [3, '2/7']], widget=widgets.RadioSelect(), blank=True)
    check1high = models.PositiveIntegerField(
        choices=[[1, '560'], [2, '522'], [3, '662']], widget=widgets.RadioSelect(), blank=True)
    check2high = models.PositiveIntegerField(
        choices=[[1, '0'], [2, '1/7'], [3, '5/7']], widget=widgets.RadioSelect(), blank=True)
    check3high = models.PositiveIntegerField(
        choices=[[1, '5/7'], [2, '1/7'], [3, '2/7']], widget=widgets.RadioSelect(), blank=True)
    check4 = models.PositiveIntegerField(
        choices=[[1, 'Not all customers can be satisfied'], [2, 'Nothing'], [3, 'Not all items can be sold']], widget=widgets.RadioSelect(), blank=True)
    check5 = models.PositiveIntegerField(
        choices=[[1, '£0.11'], [2, '£11.30'], [3, '£1.13']], widget=widgets.RadioSelect(), blank=True)
    pecu = models.PositiveIntegerField(
        choices=[[1, '1 = Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9 = As much as possible']], widget=widgets.RadioSelect())
    nonpecu = models.PositiveIntegerField(
        choices=[[1, '1 = Not at all'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9 = As much as possible']], widget=widgets.RadioSelect())
    conflict = models.PositiveIntegerField(
        choices=[[1, '1 = Least conflicted'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6'], [7, '7'], [8, '8'], [9, '9 = Most conflicted']], widget=widgets.RadioSelect())
