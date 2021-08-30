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
import random

author = 'IL'

doc = """
Supply Chain Sourcing Game, adapted from https://doi.org/10.1111/j.1540-4609.2012.00368.x
Two players, one is retailer, the other is wholesale
The purpose is to come to an agreement on supplying goods from the wholesaler to the retailer over four months
Three rounds, game ends in a round if retailer's offer is accepted by the wholesaler
Retailers move first by submitting a request for quotation (RFQ) form to the supplier
Free-form comments are allowed side-to-side
Retailer demand is randomly generated from two options that slightly differ
"""


def isordermade(order):

    if (order > 0):
        ordermade = 1
    else:
        ordermade = 0

    return ordermade


def retailerprofits(wholesaleprice, may, jun, jul, aug, demand):

    mayinventory = may
    juninventory = jun + max(mayinventory - demand[0],0)
    julinventory = jul + max(juninventory - demand[1],0)
    auginventory = aug + max(julinventory - demand[2],0)
    salinventory = max(auginventory - demand[3],0)

    mayprofits = Constants.rprice * min(mayinventory, demand[0]) - Constants.rordercost * isordermade(may) - wholesaleprice * may - Constants.rholdingcost * mayinventory
    junprofits = Constants.rprice * min(juninventory, demand[1]) - Constants.rordercost * isordermade(jun) - wholesaleprice * jun - Constants.rholdingcost * juninventory
    julprofits = Constants.rprice * min(julinventory, demand[2]) - Constants.rordercost * isordermade(jul) - wholesaleprice * jul - Constants.rholdingcost * julinventory
    augprofits = Constants.rprice * min(auginventory, demand[3]) - Constants.rordercost * isordermade(aug) - wholesaleprice * aug - Constants.rholdingcost * auginventory
    salvageprofit = Constants.salvageprice * salinventory

    return mayprofits+junprofits+julprofits+augprofits+salvageprofit


def wholesalerprofits(wholesaleprice, may, jun, jul, aug):

    mayprofits = wholesaleprice * may - Constants.wordercost * isordermade(may) - Constants.wunitcost * may - Constants.wholdingcost * may
    junprofits = wholesaleprice * jun - Constants.wordercost * isordermade(jun) - Constants.wunitcost * jun - Constants.wholdingcost * jun
    julprofits = wholesaleprice * jul - Constants.wordercost * isordermade(jul) - Constants.wunitcost * jul - Constants.wholdingcost * jul
    augprofits = wholesaleprice * aug - Constants.wordercost * isordermade(aug) - Constants.wunitcost * aug - Constants.wholdingcost * aug

    return mayprofits + junprofits + julprofits + augprofits


class Constants(BaseConstants):

    name_in_url = 'supplychain'
    players_per_group = 2
    # round 1 is only used by Retailers to send the initial RFQ
    # the true first mover in a round is the Wholesaler, but his move is suppressed in round 1
    # the Wholesaler always reacts to the RFQ sent by the Retailer in the previous round
    num_rounds = 4
    instructions_template = 'supplychain/Instructions.html'
    retailerinfo_template = 'supplychain/Retailerinfo.html'
    wholesalerinfo_template = 'supplychain/Wholesalerinfo.html'
    retailerprofitcalculator = 'supplychain/profitcalculatorR.html'
    wholesalerprofitcalculator = 'supplychain/profitcalculatorW.html'

    rholdingcost = 3
    rordercost = 2000
    rprice = 60
    salvageprice = 31

    wholdingcost = 2
    wordercost = 5000
    wunitcost = 30


class Subsession(BaseSubsession):

    def creating_session(self):

        if random.random() < .5:
            self.session.vars['demand'] = [750,2000,750,1500]
        else:
            self.session.vars['demand'] = [700,2100,800,1400]


class Group(BaseGroup):

    retaileraccept = models.StringField(choices=['Accept', 'Reject'], initial='', widget=widgets.RadioSelect, label='')

    # retailer order quantities in the Request for Quotation form
    orderQ_May = models.IntegerField(min=0, label="")
    orderQ_June = models.IntegerField(min=0, label="")
    orderQ_July = models.IntegerField(min=0, label="")
    orderQ_August = models.IntegerField(min=0, label="")
    retailercomment = models.LongStringField(label="", blank=True)

    # wholesaler response to retailer RFQ
    supplyQ_May = models.IntegerField(min=0, label="")
    supplyQ_June = models.IntegerField(min=0, label="")
    supplyQ_July = models.IntegerField(min=0, label="")
    supplyQ_August = models.IntegerField(min=0, label="")
    wholesaleprice = models.FloatField(min=0, label="Wholesale price")
    wholesalercomment = models.LongStringField(label="", blank=True)

    wprofit = models.FloatField()
    rprofit = models.FloatField()


class Player(BasePlayer):
    pass
