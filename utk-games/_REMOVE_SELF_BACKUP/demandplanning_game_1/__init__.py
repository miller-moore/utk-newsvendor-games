from pathlib import Path

import pandas as pd
from otree.api import BaseConstants, BaseSubsession, Currency
from otree.session import Session

from . import util
from .constants import APP_DIR, Constants
from .models import Group, Player, Subsession
from .pages import Game, Results, Welcome
from .treatment import Treatment

author = (
    "Anne Dohmen - UTK Department of Supply Chain Management, Miller Moore - UTK Department of Business Analytics & Statistics"
)

doc = """
Demand planning game to study planner biases when inventory levels are retained from period to period.
Each participant is randomly assigned to one of four treatment groups:
<ul>
    <li>Participant's demand distribution has a 'low' variance and a disruption to their demand distribution occurs in the first minigame</li>
    <li>Participant's demand distribution has a 'low' variance and a disruption to their demand distribution 'does not occur' in the first minigame</li>
    <li>Participant's demand distribution has a 'high' variance and a disruption to their demand distribution 'occurs' in the first minigame</li>
    <li>Participant's demand distribution has a 'high' variance and a disruption to their demand distribution 'does not occur' in the first minigame</li>
</ul>
<ul>
    <li>Note: all participants encounter a disruption during the 2nd playthrough at round=int(3/4 * rounds_per_minigame) </li>
    <li>Note: by random treatment assignment, some participants also experience a disruption during the first playthrough which occurs during round=int(1/4 * rounds_per_minigame)</li>
</ul>

"""


def creating_session(subsession: BaseSubsession) -> None:

    from otree import settings

    print("otree.settings: %s", str(settings.__dict__))

    # demand_df = pd.read_csv(APP_DIR / "static" / "demand_distributions.csv")

    # # for player in subsession.get_players():

    # treatment = Treatment.choose()
    # subsession.session.vars["treatment"] = treatment.json()

    # if treatment.variance_option == "low":
    #     subsession.session.vars["demand"] = demand_df.d1.values.tolist()

    # else:
    #     subsession.session.vars["demand"] = demand_df.d2.values.tolist()


# main sequence of pages for this otree app
page_sequence = [Welcome, Game, Results]
