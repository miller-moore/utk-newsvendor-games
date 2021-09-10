from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from otree.api import Currency as c
from otree.api import currency_range, safe_json

from . import models
from ._builtin import Bot, Page, WaitPage
from .models import Constants, profit, set_time, trueorderquantity

# demand_distributions_csv = Path(__file__).resolve().parent / "templates" / "newsvendor" / "demand_distributions.csv"
app_directory = Path(__file__).resolve().parent
demand_distributions_csv = app_directory / "static" / "demand_distributions.csv"
if not demand_distributions_csv.exists():
    import numpy as np
    import pandas as pd

    mu, sigma1, sigma2 = 500, 50, 100
    dist1 = np.random.normal(loc=mu, scale=sigma1, size=(int(1e6),))
    dist2 = np.random.normal(loc=mu, scale=sigma2, size=(int(1e6),))
    df = pd.DataFrame({"d1": dist1, "d2": dist2})
    df.to_csv(demand_distributions_csv, header=True, index=False)


class FirstWelcomePage(Page):

    form_model = "player"
    form_fields = ["prolificcode"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player):
        return dict(
            demand_distributions_csv=str(
                Path.joinpath(Path("/"), Path(demand_distributions_csv.parent.name), Path(demand_distributions_csv.name))
            )
        )


class WelcomePage(Page):

    form_model = "player"
    form_fields = ["check1low", "check2low", "check3low", "check1high", "check2high", "check3high", "check4", "check5"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player):

        if player.session.config["margin"] == "low":
            marginlow = True
            baselinereward = "0.12"

        else:
            marginlow = False
            baselinereward = "0.20"

        return {
            "session.vars['demand']": player.session.vars.get("demand"),
            "baselinereward": baselinereward,
            "marginlow": marginlow,
            "margin": safe_json(player.session.config["margin"]),
            "label1l": "If your order quantity is 600 and the demand realization is 700, what is your profit?",
            "label2l": "If your order quantity is 600, what is the probability that your profit will be 936?",
            "label3l": "If your order quantity is 750, what is the probability that your profit will be 806?",
            "label4": "What happens if the demand is higher than your order quantity?",
            "label5": "If your average profit over all the rounds is 1130, what is your monetary reward from Part 2 (without the baseline reward)?",
            "label1h": "If your order quantity is 400 and the demand realization is 500, what is your profit?",
            "label2h": "If your order quantity is 500, what is the probability that your profit will be 700?",
            "label3h": "If your order quantity is 800, what is the probability that your profit will be 942?",
        }


class DecideOrderQuantity(Page):

    form_model = "player"
    form_fields = ["orderquantity"]

    @staticmethod
    def vars_for_template(player):
        return {"round": player.round_number, "margin": safe_json(player.session.config["margin"])}

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.endtime = set_time()
        player.demand = player.session.vars["demand"][player.round_number - 1]
        player.trueorderquantity = trueorderquantity(player.orderquantity, player.session.config["margin"])
        player.payoff = profit(player.demand, player.orderquantity, player.session.config["margin"])
        player.formatted_payoff = format(player.payoff, ".0f")


class Results(Page):
    @staticmethod
    def vars_for_template(player):

        if player.session.config["margin"] == "low":
            demand = player.session.vars["demand"][player.round_number - 1]
            demandindex = (demand - 500) / 50
        else:
            demand = player.session.vars["demand"][player.round_number - 1]
            demandindex = (demand - 300) / 100

        if demandindex < player.orderquantity:
            demandtext = "Because demand was lower than your inventory level, you have leftover units in your inventory that you could not profit from."
        elif demandindex > player.orderquantity:
            demandtext = "Because demand was higher than your inventory level, you could not satisfy all the customer demand."
        else:
            demandtext = "Your order quantity exactly matched demand."

        return {
            "round": player.round_number,
            "margin": safe_json(player.session.config["margin"]),
            "orderqindex": safe_json(player.orderquantity),
            "demand": demand,
            "demandindex": safe_json(demandindex),
            "player_in_all_rounds": player.in_all_rounds(),
            "demandtext": demandtext,
        }

    @staticmethod
    def before_next_page(player, timeout_happened: bool):
        player.starttime = set_time()


class FinalPage(Page):
    form_model = "player"
    form_fields = ["pecu", "nonpecu", "conflict"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == Constants.num_rounds

    @staticmethod
    def vars_for_template(player):

        if player.session.config["margin"] == "low":
            baselinereward = "0.12"

        else:
            baselinereward = "0.20"

        reward = Decimal(float(player.participant.payoff) / (1000 * Constants.num_rounds)).quantize(
            Decimal(".01"), rounding=ROUND_HALF_UP
        )
        return {
            "averagepay": player.participant.payoff / Constants.num_rounds,
            "reward": reward,
            "baselinereward": baselinereward,
        }


# class PageAfterFinalPage(Page):

#    def is_displayed(self):
#        return self.round_number == Constants.num_rounds

#    def vars_for_template(self):

#        return {
#            'prolificurl': self.session.config['prolificurl']
#        }


page_sequence = [
    FirstWelcomePage,
    WelcomePage,
    DecideOrderQuantity,
    Results,
    FinalPage
    #    PageAfterFinalPage,
]
