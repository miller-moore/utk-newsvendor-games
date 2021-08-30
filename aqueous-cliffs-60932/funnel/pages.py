from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import math, numpy


class InitialPage(Page):

    timeout_seconds = 0

    def before_next_page(self):

        # prevx, prevy are the location of the funnel in previous round
        if self.round_number == 1:
            prevx = 0
            prevy = 0
        else:
            prevx = self.player.in_round(self.round_number - 1).x
            prevy = self.player.in_round(self.round_number - 1).y

        # xcoord, ycoord are where the marble rolls at the start of the current round
        xcoord = numpy.ceil(numpy.random.normal(prevx, Constants.stdev))
        ycoord = numpy.ceil(numpy.random.normal(prevy, Constants.stdev))

        if xcoord > 150:
            xcoord = 150

        if xcoord < -150:
            xcoord = -150

        if ycoord > 150:
            ycoord = 150

        if ycoord < -150:
            ycoord = -150

        self.player.xcoord = xcoord
        self.player.ycoord = ycoord
        self.player.score = math.sqrt(xcoord*xcoord + ycoord*ycoord)


class MyPage(Page):

    form_model = 'player'
    form_fields = ['x','y']

    def vars_for_template(self):

        # list of coordinates for the balls, starts from the centre of the area
        allycoord = []
        allxcoord = []

        cumulativescore = 0
        i = 1
        while i < self.round_number + 1:
            allxcoord.append(self.player.in_round(i).xcoord)
            allycoord.append(self.player.in_round(i).ycoord)
            cumulativescore += self.player.in_round(i).score
            i += 1

        # prevx, prevy are the location of the funnel in previous round
        # this is the starting location of the funnel in the new round
        if self.round_number == 1:
            # 1st round is an exception: we randomly locate the funnel around the centre
            prevx = numpy.ceil(numpy.random.normal(0, Constants.stdev))
            prevy = numpy.ceil(numpy.random.normal(0, Constants.stdev))
        else:
            prevx = self.player.in_round(self.player.round_number - 1).x
            prevy = self.player.in_round(self.player.round_number - 1).y

        return {
            'allxcoord': allxcoord,
            'allycoord': allycoord,
            'round': self.player.round_number,
            'prevx': prevx,
            'prevy': prevy,
            'cumulativescore': cumulativescore
        }


class Results(Page):

    def is_displayed(self):
        return self.round_number == 10 or self.round_number == 20 or self.round_number == 30 or self.round_number == 40#Constants.num_rounds

    def vars_for_template(self):

        # list of coordinates for the balls, starts from the centre of the area
        allycoord = []
        allxcoord = []

        cumulativescore = 0
        controllimitbreach = 0 # counts how many times UCL or LCL is exceeded
        i = 1
        while i < self.round_number + 1:
            allxcoord.append(self.player.in_round(i).xcoord)
            allycoord.append(self.player.in_round(i).ycoord)
            cumulativescore += self.player.in_round(i).score
            if abs(self.player.in_round(i).xcoord) > 3*Constants.stdev:
                controllimitbreach += 1
            if abs(self.player.in_round(i).ycoord) > 3*Constants.stdev:
                controllimitbreach += 1
            i += 1

        if controllimitbreach > 3:
            controllimitbreachtext = "You have exceeded the control limits " + str(controllimitbreach) + " times. Try to be more careful in the future rounds."
            if self.round_number == Constants.num_rounds:
                controllimitbreachtext = "You have exceeded the control limits " + str(controllimitbreach) + " times."
        elif controllimitbreach > 0:
            controllimitbreachtext = "You have exceeded the control limits only " + str(controllimitbreach) + " times. Good job."
        else:
            controllimitbreachtext = "You have not exceeded the control limits even once. Excellent job!"

        # lowest score simulation, assuming funnel is kept at centre
        mclowscore = []
        for mc in range(1000):
            lowscore = 0
            for i in range(self.round_number):
                xcoord = numpy.ceil(numpy.random.normal(0, Constants.stdev))
                ycoord = numpy.ceil(numpy.random.normal(0, Constants.stdev))
                lowscore += math.sqrt(xcoord * xcoord + ycoord * ycoord)

            mclowscore.append(lowscore)

        if min(mclowscore) < .8*cumulativescore:
            lowscoretext = "You can do much better."
        else:
            lowscoretext = "Great job."

        return {
            'allxcoord': allxcoord,
            'allycoord': allycoord,
            'round': self.player.round_number,
            'lowscore': min(mclowscore),
            'lowscoretext': lowscoretext,
            'cumulativescore': cumulativescore,
            'controllimitbreach': controllimitbreach,
            'controllimitbreachtext': controllimitbreachtext
        }

page_sequence = [InitialPage, MyPage, Results]
