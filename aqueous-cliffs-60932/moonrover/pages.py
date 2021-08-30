from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, moonroverfun


class MyPage(Page):
    form_model = 'player'
    form_fields = ['startx','starty','firstsite','secondsite','thirdsite','fourthsite','fifthsite']

    def before_next_page(self):

        [yourpoints, yourdist] = moonroverfun(self.player.startx, self.player.starty, self.player.firstsite, self.player.secondsite, self.player.thirdsite, self.player.fourthsite, self.player.fifthsite)

        if yourdist > 10:
            self.player.points = 0
        else:
            self.player.points = yourpoints

class Results(Page):

    def vars_for_template(self):

        [yourpoints, yourdist] = moonroverfun(self.player.startx, self.player.starty, self.player.firstsite, self.player.secondsite, self.player.thirdsite, self.player.fourthsite, self.player.fifthsite)

        text2 = ""
        if yourdist > 10:
            text = 'Unfortunately the distance was more than allowed for the drone, therefore your answer cannot be accepted. Go ahead and try again.'
        else:
            if yourpoints < 12 and yourpoints > 9:
                text = "Close! The maximum profit you could achieve is £12,000. Go ahead and try again!"
            elif yourpoints <= 9:
                text = "You could do better, go ahead and try again!"
            else:
                text = "Congratulations! You achieved the maximum profit."

        return {
            'startx': self.player.startx,
            'starty': self.player.starty,
            'firstsite': self.player.firstsite,
            'secondsite': self.player.secondsite,
            'thirdsite': self.player.thirdsite,
            'fourthsite': self.player.fourthsite,
            'fifthsite': self.player.fifthsite,
            'text': text,
            'dist': yourdist,
            'points': yourpoints,
            'profit': '£' + str(yourpoints) + ',000'
        }


page_sequence = [
    MyPage,
    Results
]
