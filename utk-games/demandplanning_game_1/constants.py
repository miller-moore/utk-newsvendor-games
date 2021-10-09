from pathlib import Path

from otree.api import BaseConstants, Currency

APP_DIR = Path(__file__).resolve().parent


class Constants(BaseConstants):
    name_in_url = APP_DIR.name
    num_rounds = 24
    players_per_group = 1
    instructions_template = f"{APP_DIR.name}/templates/includes/instructions.html"
    endowment = Currency(0)

    # custom constants
    app_name = APP_DIR.name
    game_number = int(APP_DIR.name.split("_")[-1])
    title_template = f"{APP_DIR.name}/templates/includes/title.html"
    demand_data_csv = str(APP_DIR / "static" / "demand_distributions.csv")


Path(Constants.demand_data_csv).parent.mkdir(parents=True, exist_ok=True)
