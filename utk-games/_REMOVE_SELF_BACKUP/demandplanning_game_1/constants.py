from pathlib import Path

import numpy as np
from otree.api import BaseConstants, Currency

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)


class Constants(BaseConstants):
    name_in_url = APP_DIR.name
    num_rounds = 24
    players_per_group = None
    instructions_template = f"{APP_DIR.name}/templates/includes/instructions.html"
    endowment = Currency(0)

    # custom constants
    app_name = APP_DIR.name
    game_number = int(APP_DIR.name.split("_")[-1])
    title_template = f"{APP_DIR.name}/templates/includes/title.html"
    static_path = str(Path.joinpath(Path("/"), Path(STATIC_DIR.parent.name)))
