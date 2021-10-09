import time
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Optional, Type

from otree.api import Page, safe_json

from . import util
from .demand import maybe_write_demand_data_csv
from .models import Constants, Player
from .treatment import Treatment


def get_page_name(page_cls: Type) -> str:
    assert (
        type(page_cls) is type and Page in page_cls.mro()
    ), f"""page does not inherit from otree.api.Page - got type {type(page_cls)} (value: {page_cls!r})"""
    return page_cls.__qualname__


def default_vars_for_template(self: Page, player: Player) -> dict:
    _vars = dict(
        page_name=get_page_name(self.__class__),
        session_name=player.session.session_name,  # NOTE: See ../settings.py - can use `session.vars.get` syntax also
        some_other_session_field=player.session.some_other_session_field,
        participantid=player.participantid,
    )
    return _vars


Page.vars_for_template = default_vars_for_template


class Welcome(Page):

    form_model = "player"
    form_fields = ["participantid"]

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool = False) -> None:
        super().before_next_page(player, timeout_happened)

        t = util.get_time()
        player.starttime = t
        player.starttime_iso = util.get_isotime(t)

        treatment = Treatment.choose()
        player.participant.treatment = treatment.to_json()

        maybe_write_demand_data_csv(data=treatment.rvs(), participantid=player.participantid)

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    def vars_for_template(self, player: Player) -> dict:
        _vars = super().vars_for_template(player)
        # assign new vars here: _vars.update(...)
        return _vars


class Game(Page):

    form_model = "player"
    form_fields = []

    @staticmethod
    def is_displayed(player: Player):
        # Game page occurs for Constants.num_rounds beginning with 2 (round 1 is page Welcome)
        return player.in_rounds(2, Constants.num_rounds + 2)

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool = False) -> None:
        super().before_next_page(player, timeout_happened)

        if player.in_round(Constants.num_rounds + 2):
            t = util.get_time()
            player.endtime = t
            player.endtime_iso = util.get_isotime(t)


class Results(Page):

    form_model = "player"
    form_fields = []

    @staticmethod
    def is_displayed(player):
        # Results occurs after `2 + Constants.num_rounds` rounds
        return player.in_round(Constants.num_rounds + 1)

    def vars_for_template(self, player: Player) -> dict:
        _vars = super().vars_for_template(player)
        _vars.update(endtime=player.endtime, endtime_iso=player.endtime_iso)
        return _vars


# class WelcomePage(Page):

#     form_model = "player"
#     form_fields = ["check1low", "check2low", "check3low", "check1high", "check2high", "check3high", "check4", "check5"]

#     @staticmethod
#     def is_displayed(player):
#         return player.round_number == 1

#     @staticmethod
#     def vars_for_template(player):

#         if player.session.config["variance_option"] == "low":
#             variance_is_low = True
#             baselinereward = "0.12"

#         else:
#             variance_is_low = False
#             baselinereward = "0.20"

#         return {
#             "session.vars['demand']": player.session.vars.get("demand"),
#             "baselinereward": baselinereward,
#             "variance_is_low": variance_is_low,
#             "variance_option": safe_json(player.session.config["variance_option"]),
#             "label1l": "If your order quantity is 600 and the demand realization is 700, what is your profit?",
#             "label2l": "If your order quantity is 600, what is the probability that your profit will be 936?",
#             "label3l": "If your order quantity is 750, what is the probability that your profit will be 806?",
#             "label4": "What happens if the demand is higher than your order quantity?",
#             "label5": "If your average profit over all the rounds is 1130, what is your monetary reward from Part 2 (without the baseline reward)?",
#             "label1h": "If your order quantity is 400 and the demand realization is 500, what is your profit?",
#             "label2h": "If your order quantity is 500, what is the probability that your profit will be 700?",
#             "label3h": "If your order quantity is 800, what is the probability that your profit will be 942?",
#         }


# class DecideOrderQuantity(Page):

#     form_model = "player"
#     form_fields = ["orderquantity"]

#     @staticmethod
#     def vars_for_template(player):
#         return {"round": player.round_number, "variance_option": safe_json(player.session.config["variance_option"])}

#     @staticmethod
#     def before_next_page(player, timeout_happened):
#         player.endtime = get_time()
#         player.demand = player.session.vars["demand"][player.round_number - 1]
#         player.trueorderquantity = trueorderquantity(player.orderquantity, player.session.config["variance_option"])
#         player.payoff = profit(player.demand, player.orderquantity, player.session.config["variance_option"])
#         player.formatted_payoff = format(player.payoff, ".0f")


# class Results(Page):
#     @staticmethod
#     def vars_for_template(player):

#         if player.session.config["variance_option"] == "low":
#             demand = player.session.vars["demand"][player.round_number - 1]
#             demandindex = (demand - 500) / 50
#         else:
#             demand = player.session.vars["demand"][player.round_number - 1]
#             demandindex = (demand - 300) / 100

#         if demandindex < player.orderquantity:
#             demandtext = "Because demand was lower than your inventory level, you have leftover units in your inventory that you could not profit from."
#         elif demandindex > player.orderquantity:
#             demandtext = "Because demand was higher than your inventory level, you could not satisfy all the customer demand."
#         else:
#             demandtext = "Your order quantity exactly matched demand."

#         return {
#             "round": player.round_number,
#             "variance_option": safe_json(player.session.config["variance_option"]),
#             "orderqindex": safe_json(player.orderquantity),
#             "demand": demand,
#             "demandindex": safe_json(demandindex),
#             "player_in_all_rounds": player.in_all_rounds(),
#             "demandtext": demandtext,
#         }

#     @staticmethod
#     def before_next_page(player, timeout_happened: bool):
#         player.starttime = get_time()


# class FinalPage(Page):
#     form_model = "player"
#     form_fields = ["pecu", "nonpecu", "conflict"]

#     @staticmethod
#     def is_displayed(player):
#         return player.round_number == Constants.num_rounds

#     @staticmethod
#     def vars_for_template(player):

#         if player.session.config["variance_option"] == "low":
#             baselinereward = "0.12"

#         else:
#             baselinereward = "0.20"

#         reward = Decimal(float(player.participant.payoff) / (1000 * Constants.num_rounds)).quantize(
#             Decimal(".01"), rounding=ROUND_HALF_UP
#         )
#         return {
#             "averagepay": player.participant.payoff / Constants.num_rounds,
#             "reward": reward,
#             "baselinereward": baselinereward,
#         }


# class PageAfterFinalPage(Page):

#    def is_displayed(self):
#        return self.round_number == Constants.num_rounds

#    def vars_for_template(self):
#        return {}


# page_sequence = [
#     FirstWelcomePage,
#     WelcomePage,
#     DecideOrderQuantity,
#     Results,
#     FinalPage
#     #    PageAfterFinalPage,
# ]
