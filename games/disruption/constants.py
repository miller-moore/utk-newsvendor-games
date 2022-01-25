from pathlib import Path

from otree.api import BaseConstants, Currency
from otree.constants import BaseConstantsMeta

GAMES = 2
ROUNDS_PER_GAME = 12

# NOTE: disruption stuff
# NOTE: a disruption only applies to the first game - everybody gets a disruption in the second game
ALLOW_DISRUPTION = True
DISRUPTION_ROUND_IN_GAMES = {1: int(1 + 1 / 2 * ROUNDS_PER_GAME), 2: int(1 + 1 / 2 * ROUNDS_PER_GAME)}
NATURAL_MEAN = 500

RVS_SIZE = int(1e5)
APP_DIR = Path(__file__).resolve().parent
APP_NAME = APP_DIR.name
STATIC_DIR = (APP_DIR / ".." / "_static" / APP_NAME).resolve()
INCLUDES_DIR = APP_DIR / "includes"


for dr in [STATIC_DIR, INCLUDES_DIR]:
    dr.mkdir(parents=True, exist_ok=True)
del dr


def get_includable_template_path(template_filepath: str) -> str:
    """Parse template_filepath to an "includable" template path, e.g., {{ include "<APP_NAME>/style.html" }} or {{ include C.STYLE_TEMPLATE }}."""
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


class C(ConstantsBase):
    # otree constants
    NAME_IN_URL = APP_NAME
    NUM_ROUNDS = GAMES * ROUNDS_PER_GAME
    PLAYERS_PER_GROUP = None
    ENDOWMENT = Currency(0)
    INSTRUCTIONS_TEMPLATE = None

    # custom constants
    NUM_GAMES = GAMES
    ROUNDS_PER_GAME = ROUNDS_PER_GAME
    APP_NAME = APP_NAME
    ALLOW_DISRUPTION = ALLOW_DISRUPTION
    RVS_SIZE = RVS_SIZE

    # paths for templates used in include tags, e.g., {{ include "disruption/style.html" }} or {{ include C.STYLE_TEMPLATE }}
    STYLE_TEMPLATE = get_includable_template_path("style.html")
    SCRIPTS_TEMPLATE = get_includable_template_path("scripts.html")
    SECTIONS_TEMPLATE = get_includable_template_path("sections.html")


if not hasattr(ConstantsBase, "__setattr__"):
    ConstantsBase.__setattr__ = orig_constants_meta_setattr
