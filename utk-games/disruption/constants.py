from pathlib import Path

GAMES = 2
ROUNDS = 12

# NOTE: disruption stuff
# NOTE: a disruption only applies to the first game - everybody gets a disruption in the second game
ALLOW_DISRUPTION = True
DISRUPTION_ROUND_IN_GAMES = {1: int(1 / 2 * ROUNDS), 2: int(1 / 2 * ROUNDS)}
VARIABILITY_CHOICES = ["high", "low"]
DISRUPTION_CHOICES = [True, False]
NATURAL_MEAN = 500

RVS_SIZE = int(1e5)
APP_DIR = Path(__file__).resolve().parent
APP_NAME = APP_DIR.name
STATIC_DIR = APP_DIR / "static"
INCLUDES_DIR = APP_DIR / "includes"


for dr in [STATIC_DIR, INCLUDES_DIR]:
    dr.mkdir(parents=True, exist_ok=True)
del dr
