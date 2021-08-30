from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
)

import csv

author = 'IL'

doc = """
Stock Control Game to teach EOQ principles and ABC classification
"""


def optimalcost(itemtype, d):
    # itemtype = 0 for Gold, 1 for silver, 2 for Bronze
    # d = day

    EOQ = [10, 47, 74]
    H = [120/365, 5/365, 2/365]

    stock = 10
    TC = []
    cumulTC = 0
#    for i in range(50): # this counts 49 days
    for i in range(d+1):
        day = i + 1

        HC = H[itemtype] * stock  # holding cost of the gold item

        if stock < 3:
            order = EOQ[itemtype]  # EOQ of the gold item
            OC = 5
        else:
            order = 0
            OC = 0

        TC.append(OC + HC)
        cumulTC += HC + OC

        stock = stock + order - 3  # demand

    return cumulTC - OC # TC[d-1]


class Constants(BaseConstants):
    name_in_url = 'eoq'
    players_per_group = None
    num_rounds = 49  # days, MAX=364
    instructions_template = 'eoq/Instructions.html'
    price = [300, 12.5, 5] # value of the item, only needed for reference to the holding cost
    ordercost = 5  # per batch
    holdingcost = [120, 5, 2] # THIS SHOULD BE 40% OF PRICE
    backlogcost = [480, 20, 8] # 4x holdingcost, per item per year
    initialinventory = 10 # same for all?
#    randomdemandgame = 'yes'
#    simple = 'no' # yes: only item B, no: all items

# EOQ's
    # A: 9
    # B: 44
    # C: 70
    # Jacobs Chase Example 20.2

class Subsession(BaseSubsession):

    def creating_session(self):

        if self.session.config['randomdemandgame'] == 'no':
            self.session.vars['demandA'] = [1095/365] * Constants.num_rounds  # ave daily demand 3
            self.session.vars['demandB'] = [1095/365] * Constants.num_rounds
            self.session.vars['demandC'] = [1095/365] * Constants.num_rounds

        else:
            with open('365demand.csv', newline='') as f:
                reader = csv.reader(f)
                data = list(reader)

            demaA = []
            demaB = []
            demaC = []

            for i in range(1, 365):
                demaA.append(int(data[i][0]))
                demaB.append(int(data[i][1]))
                demaC.append(int(data[i][2]))

            self.session.vars['demandA'] = demaA  # ave daily demand 3
            self.session.vars['demandB'] = demaB  # ave daily demand 3
            self.session.vars['demandC'] = demaC  # ave daily demand 3


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    QA = models.PositiveIntegerField(choices=range(101), initial=0, label="") # order quantity
    QB = models.PositiveIntegerField(choices=range(101), initial=0, label="") # order quantity
    QC = models.PositiveIntegerField(choices=range(101), initial=0, label="") # order quantity
    IA = models.FloatField()     # onhand inventory
    IB = models.FloatField()     # onhand inventory
    IC = models.FloatField()     # onhand inventory
    ocA = models.FloatField()    # ordercost during current round
    hcA = models.FloatField()    # holdingcost during current round
    bcA = models.FloatField()    # backlog during current round
    ocB = models.FloatField()  # ordercost during current round
    hcB = models.FloatField()  # holdingcost during current round
    bcB = models.FloatField()  # backlog during current round
    ocC = models.FloatField()  # ordercost during current round
    hcC = models.FloatField()  # holdingcost during current round
    bcC = models.FloatField()  # backlog during current round

    freeform = models.LongStringField(label="")