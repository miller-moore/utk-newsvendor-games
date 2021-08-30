from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, wholesalerprofits, retailerprofits


class Introduction(Page):
    timeout_seconds = 600

    def is_displayed(self):
        return self.round_number == 1


class Supplier(Page):

    form_model = 'group'
    form_fields = ['supplyQ_May','supplyQ_June','supplyQ_July','supplyQ_August','wholesaleprice','wholesalercomment']

    def vars_for_template(self):

        # these are the RFQs as they come from the previous round
        if self.round_number > 1:
            prevorderQ_May = self.group.in_round(self.round_number - 1).orderQ_May
            prevorderQ_June = self.group.in_round(self.round_number - 1).orderQ_June
            prevorderQ_July = self.group.in_round(self.round_number - 1).orderQ_July
            prevorderQ_August = self.group.in_round(self.round_number - 1).orderQ_August
            prevretailercomment = self.group.in_round(self.round_number - 1).retailercomment

        else:
            prevorderQ_May = 0
            prevorderQ_June = 0
            prevorderQ_July = 0
            prevorderQ_August = 0
            prevretailercomment = 0

        return {
            'prevorderQ_May': prevorderQ_May,
            'prevorderQ_June': prevorderQ_June,
            'prevorderQ_July': prevorderQ_July,
            'prevorderQ_August': prevorderQ_August,
            'prevretailercomment': prevretailercomment,
            'roundnumber': self.round_number - 1
        }

    def is_displayed(self):
        return self.player.id_in_group == 2 and self.round_number > 1    # id 2 is the supplier


class WaitForSupplier(WaitPage):

    template_name = 'supplychain/waitpage.html'
    title_text = 'Wait for the other player'
    body_text = ''


class RetailerAccept(Page):

    form_model = 'group'
    form_fields = ['retaileraccept']

    def vars_for_template(self):

        return {
            'roundnumber': self.round_number - 1,
            'demand': self.session.vars['demand']
        }

    def is_displayed(self):
        return self.player.id_in_group == 1 and self.round_number > 1    # id 2 is the supplier

    def before_next_page(self):
        if self.group.retaileraccept == 'Accept':
            self.group.wprofit = wholesalerprofits(self.group.wholesaleprice, self.group.supplyQ_May, self.group.supplyQ_June, self.group.supplyQ_July, self.group.supplyQ_August)
            self.group.rprofit = retailerprofits(self.group.wholesaleprice, self.group.supplyQ_May, self.group.supplyQ_June, self.group.supplyQ_July, self.group.supplyQ_August, self.session.vars['demand'])
        else:
            self.group.wprofit = 0
            self.group.rprofit = 0


class RetailerRFQ(Page):

    form_model = 'group'
    form_fields = ['orderQ_May','orderQ_June','orderQ_July','orderQ_August','retailercomment']

    def vars_for_template(self):

        return {
            'roundnumber': self.round_number - 1,
            'demand': self.session.vars['demand']
        }

    def is_displayed(self):
        return self.player.id_in_group == 1 and (self.group.retaileraccept == 'Reject' or self.round_number == 1) and not self.round_number == Constants.num_rounds  # id 1 is the retailer


class ResultsWaitPage(WaitPage):

    template_name = 'supplychain/waitpage.html'
    title_text = 'Wait for the other player'
    body_text = ''
    def after_all_players_arrive(self):
        pass


class GameEnd(Page):

    def vars_for_template(self):

        return {
            'retailerloss': -self.group.rprofit,
            'wholesalerloss': -self.group.wprofit,
            'retailerprofit': self.group.rprofit,
            'wholesalerprofit': self.group.wprofit,
            'roundnumber': self.round_number - 1,
            'roundnumberp1': self.round_number,
            'roundnumbers': range(self.round_number)
        }

    def is_displayed(self):
        return self.group.retaileraccept == 'Accept' or self.round_number == Constants.num_rounds


page_sequence = [Introduction,
                 Supplier,
                 WaitForSupplier,
                 RetailerAccept,
                 RetailerRFQ,
                 ResultsWaitPage,
                 GameEnd
                 ]
