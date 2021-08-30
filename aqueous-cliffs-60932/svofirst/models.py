from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import numpy, csv

author = 'Your name here'

doc = """
SVO: 6 dictator allocations, strategy method, each has 9 options
"""

def svoscorecalc(al1,al2,al3,al4,al5,al6):
    ifile = open('svoall.csv', 'rt')
    alloc = []
    try:
        reader = csv.reader(ifile)
        for row in reader:
            alloc.append(list(map(int, row)))
    finally:
        ifile.close()

    jtable = [al1,al2,al3,al4,al5,al6]  # [al1,al2,...,al6]
    sum1 = 0
    sum2 = 0
    for i in range(0, 6):
        sum1 = sum1 + alloc[jtable[i] - 1][2 * (i)]
        sum2 = sum2 + alloc[jtable[i] - 1][2 * (i) + 1]
    mean1 = sum1 / 6 - 50
    mean2 = sum2 / 6 - 50
    svoscore = numpy.arctan(mean2 / mean1) * 180 / numpy.pi

    return svoscore


class Constants(BaseConstants):
    name_in_url = 'svofirst'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    prolificcode = models.CharField()

    allocation1 = models.PositiveIntegerField(
        choices=[1,2,3,4,5,6,7,8,9], widget=widgets.RadioSelect())

    allocation2 = models.PositiveIntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9], widget=widgets.RadioSelect())

    allocation3 = models.PositiveIntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9], widget=widgets.RadioSelect())

    allocation4 = models.PositiveIntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9], widget=widgets.RadioSelect())

    allocation5 = models.PositiveIntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9], widget=widgets.RadioSelect())

    allocation6 = models.PositiveIntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9], widget=widgets.RadioSelect())

    check1 = models.PositiveIntegerField()
    check2 = models.PositiveIntegerField()

    svoscore = models.FloatField()
