from os import terminal_size
from pathlib import Path
from string import ascii_uppercase

import pandas as pd
from otree.api import BaseConstants, BaseSubsession, Currency
from otree.session import Session
from rich import print

from . import util
from .constants import APP_DIR, Constants
from .models import Group, Player, Subsession
from .pages import Game, Results, Welcome
from .treatment import Treatment

# TODO: ADD THE HTML CHARTING CODE INTO AN INCLUDES TEMPLATE e.g. ./includes/.html
print(
    "\n",
    "[blue]TODO[/]: recover client charting code from one of the templates in the (utknewsvendor?) directory of the master branch.",
    "\n",
    "[blue]TODO[/]: things that need to be in the data card window are described in template_includes/DataCard.html." "\n\n",
)


def creating_session(subsession: BaseSubsession) -> None:

    settings = util.get_settings()

    #
    print("\notree settings:\n%s", str(settings.asdict()))

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
