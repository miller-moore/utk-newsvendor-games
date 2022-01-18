from pathlib import Path

from otree.api import BaseConstants, Currency
from otree.constants import BaseConstantsMeta

GAMES = 2
ROUNDS = 12

# NOTE: disruption stuff
# NOTE: a disruption only applies to the first game - everybody gets a disruption in the second game
ALLOW_DISRUPTION = True
DISRUPTION_ROUND_IN_GAMES = {1: int(1 + 1 / 2 * ROUNDS), 2: int(1 + 1 / 2 * ROUNDS)}
NATURAL_MEAN = 500

RVS_SIZE = int(1e5)
APP_DIR = Path(__file__).resolve().parent
APP_NAME = APP_DIR.name
STATIC_DIR = APP_DIR / ".." / "_static" / APP_NAME
INCLUDES_DIR = APP_DIR / "includes"


for dr in [STATIC_DIR, INCLUDES_DIR]:
    dr.mkdir(parents=True, exist_ok=True)
del dr


def get_includable_template_path(template_filepath: str) -> str:
    """Parse template_filepath to an "includable" template path, e.g., {{ include "<APP_NAME>/style.html" }} or {{ include Constants.style_template }}."""
    p = Path(template_filepath)
    assert (
        ".html" in p.suffixes
    ), f"""expected template_filepath extension to include {".html"!r} - got {template_filepath!r} (extension {p.suffix!r})."""

    # strict file path (must exist)
    filepath = (APP_DIR / template_filepath).resolve(strict=True)

    # return string for django include expression: {{ include "include_path" }}
    include_path = str(Path(APP_DIR.name) / filepath.name)
    return include_path


# Hack to allow settattr on Constants at runtime
if hasattr(BaseConstantsMeta, "__setattr__"):
    orig_constants_meta_setattr = BaseConstantsMeta.__setattr__
    try:
        delattr(BaseConstantsMeta, "__setattr__")
    except:
        pass


class ConstantsBase(BaseConstants, metaclass=BaseConstantsMeta):
    pass


class Constants(ConstantsBase):
    # otree constants
    name_in_url = APP_NAME
    num_rounds = GAMES * ROUNDS
    players_per_group = None
    endowment = Currency(0)
    instructions_template = None

    # custom constants
    num_games = GAMES
    rounds_per_game = ROUNDS
    app_name = APP_DIR.name
    allow_disruption = ALLOW_DISRUPTION
    rvs_size = RVS_SIZE
    prolific_code = "THIS_CODE_IS_TOTALLY_CONTRIVED"

    # paths for templates used in include tags, e.g., {{ include "disruption/style.html" }} or {{ include Constants.style_template }}
    style_template = get_includable_template_path("style.html")
    scripts_template = get_includable_template_path("scripts.html")
    sections_template = get_includable_template_path("sections.html")


if not hasattr(ConstantsBase, "__setattr__"):
    ConstantsBase.__setattr__ = orig_constants_meta_setattr
