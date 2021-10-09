from pathlib import Path

import numpy as np
from otree.api import BaseConstants, Currency

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

NUM_ROUNDS = 24


class Constants(BaseConstants):
    def _template_path(template_filename: str) -> str:
        assert template_filename.endswith(".html"), f"""template_filename does not endwith {".html"!r}"""
        return f"{APP_DIR.name}/template_includes/{template_filename}"

    name_in_url = APP_DIR.name
    num_rounds = NUM_ROUNDS
    players_per_group = None
    endowment = Currency(0)
    instructions_template = _template_path("GameInstructions.html")

    title_template = _template_path("Title.html")  # NOTE: custom member, not a member of BaseConstants
    demand_dist_template = _template_path("DemandDistribution.html")  # NOTE: custom member, not a member of BaseConstants
    data_card_template = _template_path("DataCard.html")  # NOTE: custom member, not a member of BaseConstants

    app_name = APP_DIR.name  # NOTE: custom member, not a member of BaseConstants
    game_number = int(APP_DIR.name.split("_")[-1])  # NOTE: custom member, not a member of BaseConstants
    static_path = str("/" / Path(STATIC_DIR.parent.name))  # NOTE: custom member, not a member of BaseConstants

    authors = [
        "Anne Dohmen, University of Tennessee - Knoxville, Department of Supply Chain Management",
        "Miller Moore, University of Tennessee - Knoxville, Department of Business Analytics & Statistics",
    ]

    doc = f"""
    This study is designed to better understand demand planner biases. Participants will play two demand planning games. Each game consists of { NUM_ROUNDS } rounds.

    <br><br>
    Each round represents a single period of demand planning, e.g. a single business month. In each game, excess inventory levels from prior planning periods accumulate and are not reset between periods. In each round, you choose the quantity of goods to
    purchase at the start of the period based on your expectations for market demand during the period. At the end of the period, results
    such as cumulative excess inventory levels are computed and stored for later reference as needed to calculate final results at game completion, e.g., cumulative retail, wholesale, holding costs, payoff, etc.

    <br><br>
    A statistical distribution determines the value of realized market demand in each period. At the start of each game, the planner is randomly assigned
    one of two predefined log-normal distributions which do not change between rounds of the game unless a "demand disruption" occurs, which randomly occurs
    to half of all participats of the study. The distributions are demarcated by significantly different variance magnitudes. As such, the distribution
    assigned to the player will be categorized as either the "low" or the "high" variability distribution.

    <br><br>
    A chart of the participant's distribution is displayed on the page at all times during the game and does not change during the game, unless a disruption occurs. Statistical
    demand distributions are well-characterized for many markets and therefore should be made available to game participants as similar information is
    expected to be available to industry planners in the course of their real jobs.

    <br><br>
    One of four treatment groups is assigned to each participant upon entering the study:

    <ol>
        <li>low variability distribution, game 1 disruption occurs</li>
        <li>low variability distribution, game 1 disruption does not occur</li>
        <li>high variability distribution, game 1 disruption occurs</li>
        <li>high variability distribution, game 1 disruption does not occur</li>
    </ol>

    Note:
    <ol>
        <li>In game 1, if a disruption occurs, it will occur at the start of round {int(3/4 * NUM_ROUNDS)}</li>
        <li>In game 2, a disruption occurs for all participants at the start of round {int(1/4 * NUM_ROUNDS)}</li>
    </ol>

    """
