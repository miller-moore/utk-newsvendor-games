from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import numpy, pandas, csv

author = 'IL'

doc = """
The Foundation Task -- determines a fuzzy consensus matrix for a group task
"""

# RETURN GROUP CONSENSUS ON A GIVEN PREFERENCE MATRIX
def consensus(prefmat):
    N = prefmat.shape[0]
    for k in range(N):
        # Fuzzy preference matrices
        fuzzy_prefmat = numpy.zeros((6, 6))
        for i in range(6):
            for j in range(6):
                if prefmat[k, j] + prefmat[k, i] == 0:
                    fuzzy_prefmat[j, i] = 0.5
                else:
                    fuzzy_prefmat[j, i] = prefmat[k, j] / (prefmat[k, j] + prefmat[k, i])
                fuzzy_prefmat[i, i] = 0.

        if k == 0:
            stacked_fuzzy = fuzzy_prefmat
        else:
            stacked_fuzzy = numpy.append(stacked_fuzzy, fuzzy_prefmat, axis=0)

            # R matrix alpha level
        alpha = 0.1
        Rmat = numpy.zeros((6, 6))
        for i in range(6):
            for j in range(6):
                if fuzzy_prefmat[j, i] < alpha:
                    Rmat[j, i] = 0
                else:
                    Rmat[j, i] = 1

        if k == 0:
            stacked_Rmat = Rmat
        else:
            stacked_Rmat = numpy.append(stacked_Rmat, Rmat, axis=0)

    # consensus matrix for the whole group is determined by the A matrices between 1 and 2, 1 and 3, and so on
    C = numpy.zeros((N, N))
    for i in range(N):
        for j in range(N):
            R = stacked_Rmat[i * 6:(i + 1) * 6]
            S = stacked_Rmat[j * 6:(j + 1) * 6]
            RSt = numpy.matmul(R, S.transpose())
            RRt = numpy.matmul(R, R.transpose())
            SSt = numpy.matmul(S, S.transpose())
            A = numpy.trace(RSt) / (numpy.trace(RRt) + numpy.trace(SSt) - numpy.trace(RSt))
            C[i, j] = A
        C[i, i] = 0

    # group consensus
    return numpy.trace(numpy.matmul(C, C.transpose())) / (N * (N - 1))


def consensus2(player_id):
    # SEARCH THE OTHER GROUP MEMBERS
    groups = pandas.read_excel('groups.xlsx')
    grouppi = groups.loc[groups['ID number'] == player_id]

    if grouppi.empty:
        ids_in_group2 = []
    else:
        group_of_player = grouppi.iloc[0][1]
        ids_in_group = groups.loc[groups['Group'] == group_of_player]['ID number']
        ids_in_group2 = []
        for i in range(len(ids_in_group)):
            ids_in_group2.append(ids_in_group.iloc[i])

    # SEARCH THE LATEST CHOICES OF EACH GROUP MEMBER AND CREATE PREFERENCE MATRIX
    alldata = pandas.read_csv('output.csv')
    alldata.set_index = 'id'
    choices_of_group_members = []
    for i in range(len(ids_in_group2)):
        tempdf = alldata.loc[alldata['id'] == ids_in_group2[i]]
        choicess = []
        for j in range(6):
            choicess.append(tempdf.iloc[-1][j + 2])

        choices_of_group_members.append(choicess)

    return consensus(numpy.array(choices_of_group_members))


class Constants(BaseConstants):
    name_in_url = 'foundationtask'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    code = models.CharField()
    groupp = models.CharField()

    p1 = models.IntegerField(choices=[0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460,480,500])
    p2 = models.IntegerField(choices=[0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460,480,500])
    p3 = models.IntegerField(choices=[0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460,480,500])
    p4 = models.IntegerField(choices=[0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460,480,500])
    p5 = models.IntegerField(choices=[0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460,480,500])
    p6 = models.IntegerField(choices=[0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460,480,500])

    consensus = models.FloatField()