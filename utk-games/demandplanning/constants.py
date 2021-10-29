from pathlib import Path

GAMES = 2
ROUNDS = 8
ALLOW_DISRUPTION = False
DISRUPTION_ROUND_IN_GAMES = {1: int(3 / 4 * ROUNDS), 2: int(1 / 4 * ROUNDS)}

RVS_SIZE = int(1e5)
APP_DIR = Path(__file__).resolve().parent
APP_NAME = APP_DIR.name
STATIC_DIR = APP_DIR / "static"
INCLUDES_DIR = APP_DIR / "includes"


for dr in [STATIC_DIR, INCLUDES_DIR]:
    dr.mkdir(parents=True, exist_ok=True)
del dr
