from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid4

from otree.api import BaseGroup, BasePlayer, BaseSubsession, models, widgets
from otree.templating import filters

from .constants import C
from .treatment import Treatment, UnitCosts
from .util import get_game_number, get_game_rounds, get_round_in_game, get_time

from common.template_filters import filters  # isort:skip


def hydrate_participant(player: "Player", **kwargs) -> None:

    if not "uuid" in player.participant.vars:
        treatment: Treatment = player.participant.vars.get("treatment", Treatment.choose())
        _ = treatment.get_demand_rvs()  # initializes treatment._demand_rvs

        player.participant.uuid = player.participant.vars.get("uuid", str(uuid4()))
        player.participant.starttime = get_time()
        player.participant.is_planner = player.participant.vars.get("is_planner", player.field_maybe_none("is_planner"))
        player.participant.years_as_planner = player.participant.vars.get(
            "years_as_planner", player.field_maybe_none("years_as_planner")
        )
        player.participant.job_title = player.participant.vars.get("job_title", player.field_maybe_none("job_title"))
        player.participant.does_consent = player.participant.vars.get("does_consent", player.field_maybe_none("does_consent"))
        # player.participant.prolific_id = player.participant.vars.get("prolific_id", player.field_maybe_none("prolific_id"))
        player.participant.company_name = player.participant.vars.get("company_name", player.field_maybe_none("company_name"))
        player.participant.work_country = player.participant.vars.get("work_country", player.field_maybe_none("work_country"))
        player.participant.nationality = player.participant.vars.get("nationality", player.field_maybe_none("nationality"))
        player.participant.unit_costs = treatment.get_unit_costs()
        player.participant.stock_units = 0
        player.participant.treatment = treatment
        player.participant.history = initialize_game_history()
        player.participant.game_results = []
        player.participant.payoff_round = player.field_maybe_none("payoff_round") or treatment.get_payoff_round()


def initialize_game_history() -> List[Dict[str, Any]]:
    return [
        dict(
            period=i + 1,
            ou=None,
            du=None,
            su_before=0 if i == 0 else None,
            su_after=None,
            ooq=None,
            revenue=None,
            cost=None,
            profit=None,
            cumulative_profit=None,
        )
        for i in range(C.ROUNDS_PER_GAME)
    ]


class Subsession(BaseSubsession):
    @staticmethod
    def creating_session(subsession: BaseSubsession):
        for player in subsession.get_players():
            hydrate_participant(player)

    # def vars_for_admin_report(self):
    #     """See https://otree.readthedocs.io/en/self/admin.html#customizing-the-admin-interface-admin-reports"""
    #     payoffs = sorted([p.payoff for p in self.get_players()])
    #     return dict(payoffs=payoffs)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # identifiers
    uuid = models.StringField()
    starttime = models.FloatField(min=get_time())
    endtime = models.FloatField(min=get_time())
    treatment = models.IntegerField(min=1)

    # Consent.html form fields
    is_planner = models.BooleanField(
        widget=widgets.RadioSelectHorizontal(),
        label="Are you presently employed in a demand or supply planning role?",
    )
    years_as_planner = models.IntegerField(
        label="How many years experience do you have in a demand or supply planning role?", min=0, max=70
    )
    job_title = models.StringField(label="What is your job title?")

    # prolific_id = models.StringField(
    #     label="""Please enter your Prolific ID below (e.g., 5b96601D3400a939Db45dAc9):""",
    # )
    company_name = models.StringField(label="""What company do you currently work for?""")
    work_country = models.StringField(label="""In what country do you work?""")
    nationality = models.StringField(label="""What is your nationality?""")
    does_consent = models.BooleanField(
        widget=widgets.CheckboxInput(),
        label="""By checking the box to the left you agree to participate in this experiment. The full consent form is available for download at the top of this page.""",
    )

    # player data
    game_number = models.IntegerField(min=1, initial=1)
    period_number = models.IntegerField(min=1, initial=1)

    # stock units, demand units, & order units
    su = models.IntegerField(min=0, initial=0)
    du = models.IntegerField(min=0)
    ou = models.IntegerField(min=0, max=1000, label="How many units will you order?")  # see also Decide.html

    # Optimal order quantity (see treatment.py)
    ooq = models.IntegerField(min=0)

    # retail cost per unit (revenue), wholesale cost per unit (cost), holding cost per unit (cost)
    rcpu = models.CurrencyField()
    wcpu = models.CurrencyField()
    hcpu = models.CurrencyField()
    # scpu = models.CurrencyField()

    # revenue = rcpu * du
    # cost = wcpu * ou + hcpu * su
    # profit = revenue - cost
    revenue = models.CurrencyField(initial=0)
    cost = models.CurrencyField(initial=0)
    profit = models.CurrencyField(initial=0)

    payoff_round = models.IntegerField()

    # final questions
    q1 = models.LongStringField(label="How did your decisions change between the two games?")
    q2 = models.LongStringField(label="How did your decisions change after the disruption?")
    donation_fund = models.StringField(
        widget=widgets.RadioSelect(),
        # label="""To which of the following funds would you like to donate your earnings to:""",
        choices=[
            [
                "Dr. Mary C. Holcomb Scholarship Endowment",
                "Dr. Mary C. Holcomb Scholarship Endowment: used to support women in SCM",
            ],
            [
                "Dr. Tom Mentzer Supply Chain Fund",
                "Dr. Tom Mentzer Supply Chain Fund: used to support department excellence in logistics",
            ],
            [
                "Supply Chain Management Excellence Fund",
                "Supply Chain Management Excellence Fund: used to support impactful initiatives in SCM department",
            ],
        ],
    )


# def custom_export(players: Iterable[Player]):
#     """See https://otree.readthedocs.io/en/self/admin.html#custom-data-exports"""
#     player_fields = [
#         "starttime",
#         "endtime",
#         "treatment",
#         "is_planner",
#         "years_as_planner",
#         "job_title",
#         "does_consent",
#         "prolific_id",
#         "company_name",
#         "game_number",
#         "period_number",
#         "su",
#         "ou",
#         "du",
#         "ooq",
#         "rcpu",
#         "wcpu",
#         "hcpu",
#         "revenue",
#         "cost",
#         "profit",
#         "payoff_round",
#         "payoff",
#     ]
#     yield ["id", "participant_code", *player_fields]

#     records = []
#     for p in players:
#         records.append([p.id, p.participant.code, *[getattr(p, name) for name in player_fields]])
#     records = sorted(records)
#     for r in records:
#         yield r
