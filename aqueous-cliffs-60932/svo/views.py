from . import models
from ._builtin import Page, WaitPage
from .models import Constants, svoscorecalc
import csv


#class WelcomePage(Page):
#    form_model = models.Player
#    form_fields = ['prolificcode']


class ElicitSVO(Page):
    form_model = models.Player
    form_fields = ['allocation1', 'allocation2', 'allocation3', 'allocation4', 'allocation5', 'allocation6']

    def vars_for_template(self):
        ifile = open('test.csv', 'rt')
        alloc = []
        try:
            reader = csv.reader(ifile)
            for row in reader:
                alloc.append(list(map(int,row)))
        finally:
            ifile.close()

        return {
            'alloc': alloc
        }


class Results(Page):

    form_model = models.Player
    form_fields = ['check1', 'check2']

    def vars_for_template(self):
        ifile = open('test.csv', 'rt')
        alloc = []
        try:
            reader = csv.reader(ifile)
            for row in reader:
                alloc.append(list(map(int,row)))
        finally:
            ifile.close()

        return {
            'alloc': alloc,
            'alloc2': self.player.allocation2
        }

    def before_next_page(self):
        al1 = self.player.allocation1
        al2 = self.player.allocation2
        al3 = self.player.allocation3
        al4 = self.player.allocation4
        al5 = self.player.allocation5
        al6 = self.player.allocation6

        self.player.svoscore = svoscorecalc(al1,al2,al3,al4,al5,al6)


class PageAfterFinalPage(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):

        return {
            'prolificurl': self.session.config['prolificurl']
        }


page_sequence = [
#    WelcomePage,
    ElicitSVO,
    Results,
    PageAfterFinalPage
]
