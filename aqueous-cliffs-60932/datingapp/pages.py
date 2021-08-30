from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class MyPage(Page):
    form_model = 'player'
    form_fields = ['Chloe','Emily','Megan','Charlotte','Jessica','Lauren','Sophie','Olivia','Hannah','Lucy']

class Results(Page):

    def vars_for_template(self):

        beforetext =""
        correct = ""
        points = 0
        if (self.player.Emily == "Jack"):
            correct = correct + "Jack with Emily, "
            points = points + 1
        if (self.player.Megan == "Thomas"):
            correct = correct + "Thomas with Megan, "
            points = points + 1
        if (self.player.Olivia == "James"):
            correct = correct + "James with Olivia, "
            points = points + 1
        if (self.player.Lucy == "Joshua"):
            correct = correct + "Joshua with Lucy, "
            points = points + 1
        if (self.player.Sophie == "Daniel"):
            correct = correct + "Daniel with Sophie, "
            points = points + 1
        if (self.player.Chloe == "Harry"):
            correct = correct + "Harry with Chloe, "
            points = points + 1
        if (self.player.Jessica == "Samuel"):
            correct = correct + "Samuel with Jessica, "
            points = points + 1
        if (self.player.Hannah == "Joseph"):
            correct = correct + "Joseph with Hannah, "
            points = points + 1
        if (self.player.Lauren == "Matthew"):
            correct = correct + "Matthew with Lauren, "
            points = points + 1
        if (self.player.Charlotte == "Callum"):
            correct = correct + "Callum with Charlotte, "
            points = points + 1
        if (correct == ""):
            correct = "You did not have any correct matches."

        if points > 0:
            beforetext = "You correctly matched: "

        return {
            'beforetext': beforetext,
            'correct': correct,
            'points': points
        }


page_sequence = [
    MyPage,
    Results
]
