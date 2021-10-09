from pathlib import Path

import pandas as pd
from otree.api import BaseConstants, BaseSubsession, Currency
from otree.session import Session

from .constants import APP_DIR, Constants
from .models import Group, Player, Subsession
from .pages import GamePage, WelcomePage
from .treatment import Treatment
from .util import maybe_write_demand_distributions_csv

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

    from otree.api import settings

    print("otree.settings: %s", str(settings.__dict__))

    # demand_df = pd.read_csv(APP_DIR / "static" / "demand_distributions.csv")

    # # for player in subsession.get_players():

    # treatment = Treatment.choose()
    # subsession.session.vars["treatment"] = treatment.json()

    # if treatment.variance_option == "low":
    #     subsession.session.vars["demand"] = demand_df.d1.values.tolist()

    # else:
    #     subsession.session.vars["demand"] = demand_df.d2.values.tolist()


# TODO(add demand data to vars_for_template instead of this hack)
# hack to make demand data available as static csv file in APP_DIR / "static" / "demand_distributions.csv"
maybe_write_demand_distributions_csv()

#
page_sequence = [WelcomePage, GamePage]
