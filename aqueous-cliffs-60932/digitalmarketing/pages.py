from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class MyPage(Page):
    form_model = 'player'
    form_fields = ['shoes','handbag']


class Results(Page):

    def vars_for_template(self):
        # these are based on demo IG follower numbers
        points = 0
        shoes = ['IG1','IG2','IG3','IG4']
        handbag = ['IG1','IG2','IG3','IG4']
        followers = ['1810','1760','1200','1450']
        for i in range(4):
            for j in range(4):
                if self.player.shoes == shoes[i] and self.player.handbag == handbag[j]:
                    points = 5000+int(followers[i]) + 3600+int(followers[j])

        return {
            'points': points
        }


page_sequence = [
    MyPage,
    Results
]
