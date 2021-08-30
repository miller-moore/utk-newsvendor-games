from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class MyPage(Page):
    form_model = 'player'
    form_fields = ['choices']

    def vars_for_template(self):

        return {
            'names': Constants.names
        }


class Results(Page):

    def vars_for_template(self):

        ch = self.player.choices
        ch = ch.split(',')
        ch = ch[1:]

        chtext = ''
        for i in range(len(ch) - 1):
            chtext += ch[i] + ', '

        if len(ch) > 1:
            chtext += ' and ' + ch[-1]
        else:
            chtext += ch[-1]

        roi = [.081,.09,.11,.102,.105,.141,.132]
        vol = [125,150,200,40,40,20,100]
        cost = [6,12,20,14,15,2,32]

        totroi = 0
        totcost = 0
        totvol = 0
        for j in range(len(ch)):
            if ch[j] in Constants.names:
                ind = Constants.names.index(ch[j])
                totroi = totroi + roi[ind]*cost[ind]*1000
                totcost = totcost + cost[ind]
                totvol = totvol + vol[ind]

        result = ''

        if len(ch)<3:
            result = 'You did not have three influcencers on board, which was the client requirement. Try again.'
        elif totcost > 45:
            result = 'Your total cost exceeds the budget. Try again.'
        elif totvol > 420:
            result = 'Your total marketing volume exceeds the limit. Try again.'
        # constraint 2
        elif Constants.names[3] in ch and Constants.names[4] in ch:
            result = 'You included both ' + Constants.names[3] + ' and ' + Constants.names[4] + ', which is against the client requirement. Try again.'
        # constraint 3
        elif Constants.names[1] in ch and not Constants.names[5] in ch:
            result = 'You included ' + Constants.names[1] + ' without also including ' + Constants.names[5] + ' which is against the client requirement. Try again.'
        elif totroi == 4261:
            result = 'Congratulations, you found the optimal solution!'
        else:
            result = 'Your solution is good but it is not the optimal. Try again.'

        return {
            'ch': ch,
            'chtext': chtext,
            'totroi': f'{int(totroi):,}',
            'totvol': totvol,
            'totcost': totcost,
            'result': result
        }


page_sequence = [MyPage, Results]
