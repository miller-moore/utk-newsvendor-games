from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, consensus2
import csv, pandas


class FirstPage(Page):

    form_model = 'player'
    form_fields = ['code']


class MyPage(Page):

    form_model = 'player'
    form_fields = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6']

    def error_message(self, values):
        if values['p1'] + values['p2'] + values['p3'] + values['p4'] + values['p5'] + values['p6'] > 500:
            return 'You are exceeding the budget!'

    def before_next_page(self):
        #df = pandas.read_csv('output.csv')
        #df.set_index = 'id'
        #newdf = df.loc[df['id'] == self.player.code]
        #group_of_player = newdf.iloc[-1][1]

        # fetch group of player
        groups = pandas.read_excel('groups.xlsx')
        grouppi = groups.loc[groups['ID number'] == self.player.code]
        if grouppi.empty:
            group_of_player = 'No group'
        else:
            group_of_player = grouppi.iloc[0][1]

        self.player.groupp = group_of_player
        # create data to be saved in output.csv
        data = [[self.player.code, group_of_player,
                 self.player.p1, self.player.p2, self.player.p3, self.player.p4, self.player.p5, self.player.p6]]
        newdfrow = pandas.DataFrame(data, columns=['id', 'group', 'project1', 'project2',
                                                   'project3', 'project4', 'project5', 'project6'])
        newdfrow.to_csv('output.csv', mode='a', header=None, index=False)


class Results(Page):

    def vars_for_template(self):

        if self.player.group == 'No group':
            self.player.consensus = 'NA'
            cons = 'NA'
        else:
            cons = consensus2(self.player.code)
            self.player.consensus = cons

        return {
            'cons': cons,
            'returnurl': self.session.config['returnurl']
        }

page_sequence = [
    FirstPage,
    MyPage,
    Results
]
