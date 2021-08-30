from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class WelcomePage(Page):
    form_model = 'player'
    form_fields = ['appchoice']


class MyPage(Page):

    timeout_seconds = 0.1

    # https://otree.readthedocs.io/en/latest/pages.html#app-after-this-page
    def app_after_this_page(self, upcoming_apps):
        if self.player.appchoice == 'Dating App':
            return "datingapp"
        elif self.player.appchoice == 'Digital Marketing':
            return "influencers"
        elif self.player.appchoice == 'Moonrover':
            return "moonrover"


page_sequence = [
    WelcomePage,
    MyPage
]
