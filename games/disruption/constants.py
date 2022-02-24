from pathlib import Path

from otree.api import BaseConstants, Currency
from otree.constants import BaseConstantsMeta

from common.utils import get_includable_template_path  # isort:skip

NUM_GAMES = 2
ROUNDS_PER_GAME = 12
RVS_SIZE = int(1e5)

APP_DIR = Path(__file__).resolve().parent
APP_NAME = APP_DIR.name
STATIC_DIR = (APP_DIR / ".." / "_static" / APP_NAME).resolve()
INCLUDES_DIR = APP_DIR / "includes"
SHOW_SMOKEY_IMAGES = False

# NOTE: disruption stuff
# NOTE: a disruption only applies to the first game - everybody gets a disruption in the second game
ALLOW_DISRUPTION = True
DISRUPTION_ROUND_IN_GAMES = {1: int(1 + 1 / 2 * ROUNDS_PER_GAME), 2: int(1 + 1 / 2 * ROUNDS_PER_GAME)}

for dr in [STATIC_DIR, INCLUDES_DIR]:
    dr.mkdir(parents=True, exist_ok=True)
del dr


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
    NUM_ROUNDS = NUM_GAMES * ROUNDS_PER_GAME
    PLAYERS_PER_GROUP = None
    ENDOWMENT = Currency(0)
    INSTRUCTIONS_TEMPLATE = None

    # custom constants
    NUM_GAMES = NUM_GAMES
    ROUNDS_PER_GAME = ROUNDS_PER_GAME
    APP_NAME = APP_NAME
    RVS_SIZE = RVS_SIZE
    STATIC_DIR = STATIC_DIR
    INCLUDES_DIR = INCLUDES_DIR
    SHOW_SMOKEY_IMAGES = SHOW_SMOKEY_IMAGES
    ALLOW_DISRUPTION = ALLOW_DISRUPTION
    DISRUPTION_ROUND_IN_GAMES = DISRUPTION_ROUND_IN_GAMES

    # paths for templates used in include tags, e.g., {{ include "disruption/style.html" }} or {{ include C.STYLE_TEMPLATE }}
    STYLE_TEMPLATE = get_includable_template_path("../common/style.html", APP_DIR)
    SCRIPTS_TEMPLATE = get_includable_template_path("scripts.html", APP_DIR)
    SECTIONS_TEMPLATE = get_includable_template_path("sections.html", APP_DIR)


if not hasattr(ConstantsBase, "__setattr__"):
    ConstantsBase.__setattr__ = orig_constants_meta_setattr
