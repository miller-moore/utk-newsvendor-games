from otree import database as models
from otree.api import BaseConstants, BaseGroup, BasePlayer, BaseSubsession, Currency, Page, WaitPage

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = "my_public_goods"
    players_per_group = 3
    num_rounds = 1
    multiplier = 2
    endowment = Currency(1000)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()


class Player(BasePlayer):
    contribution = models.CurrencyField(min=0, max=Constants.endowment, label="How much will you contribute?")


# PAGES
class Contribute(Page):
    form_model = "player"
    form_fields = ["contribution"]


def set_payoffs(group):
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = group.total_contribution * Constants.multiplier / Constants.players_per_group
    for player in players:
        player.payoff = Constants.endowment - player.contribution + group.individual_share


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = "set_payoffs"


class Results(Page):
    pass


page_sequence = [Contribute, ResultsWaitPage, Results]
