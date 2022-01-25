import json
import random
import traceback
from enum import Enum, Flag
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import (AbstractSet, Any, Callable, Dict, List, Mapping, Optional,
                    Tuple, Union)

import numpy as np
import scipy.stats as stats
from otree.api import BasePlayer, Currency
from otree.currency import _CurrencyEncoder
from pydantic import BaseModel, Field, StrBytes, typing, validator
from pydantic.main import Extra
from pydantic.types import conint

from .constants import DISRUPTION_ROUND_IN_GAMES, NATURAL_MEAN, STATIC_DIR, C
from .pydanticmodel import PydanticModel
from .util import (get_round_in_game, lognormalize_normal_samples,
                   normalize_lognormal_samples)


class VariabilityDegree(str, Enum):
    LOW = "low"
    HIGH = "high"


class DisruptionGameOne(Flag):
    TRUE = True
    FALSE = False


# NOTE: mapping of treatment parameters, values are all combinations of VariabilityDegree x DisruptionGameOne, keys are treatment indexes (1-4)
# {1: ('low', True), 2: ('low', False), 3: ('high', True): 4: ('high', False) }
TREATMENT_MAP: Dict[int, Tuple[VariabilityDegree, DisruptionGameOne]] = {
    i + 1: params for i, params in enumerate(product(list(VariabilityDegree), list(DisruptionGameOne)))
}

# NOTE: use lru cache to save time when making repeated calls because drawing large samples is slow
@lru_cache(maxsize=10)
def sample_normal_rvs(mu: float, sigma: float, size: int = int(1e4)) -> List[float]:
    return np.random.normal(loc=mu, scale=sigma, size=size).tolist()


class Distribution(PydanticModel):
    mu: float
    sigma: float

    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "UnitCosts":
        if treatment.variance_choice == "low":
            if not treatment.is_disrupted():
                mu, sigma = 500, 50
            else:
                mu, sigma = 500, 100
        else:
            if not treatment.is_disrupted():
                mu, sigma = 500, 100
            else:
                mu, sigma = 500, 200

        return Distribution(mu=mu, sigma=sigma)


class UnitCosts(PydanticModel):
    rcpu: Currency  # retail cost / unit (revenue)
    wcpu: Currency  # wholesale cost / unit (order cost)
    hcpu: Currency  # holding cost / unit (stock cost)

    class Config:
        json_encoders = dict(Currency=_CurrencyEncoder)
        arbitrary_types_allowed = True

    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "UnitCosts":
        return UnitCosts(rcpu=15.0, wcpu=6.0, hcpu=1.0)


class Treatment(PydanticModel):
    idx: conint(strict=True, ge=1, le=len(TREATMENT_MAP))
    _demand_rvs: List[float] = []
    _disrupted: bool = False
    _disrupted_png_file: Path = None
    _distribution: Distribution = None
    _png_file: Path = None
    _payoff_round: int = None

    class Config:
        extra = Extra.allow

    def reset(self):
        size = len(self._demand_rvs) if self._demand_rvs else C.RVS_SIZE
        self._demand_rvs = self.get_demand_rvs(size=size)
        self._disrupted = False
        self._disrupted_png_file: Path = None
        self._distribution = None
        self._png_file: Path = None
        self._payoff_round: int = None

    @classmethod
    def from_json(cls, json: StrBytes) -> "Treatment":
        return Treatment.parse_raw(json)

    @property
    def variance_choice(self) -> str:
        return TREATMENT_MAP[self.idx][0].value

    @property
    def disruption_choice(self) -> bool:
        return TREATMENT_MAP[self.idx][1].value

    @classmethod
    def choose(cls) -> "Treatment":
        return Treatment(idx=random.choice(list(TREATMENT_MAP)))

    def disrupt(self) -> None:
        self._disrupted = True

    def is_disrupted(self) -> bool:
        return self._disrupted

    def get_unit_costs(self) -> UnitCosts:
        return UnitCosts.from_treatment(self)

    def get_distribution(self) -> Distribution:
        return Distribution.from_treatment(self)

    def get_payoff_round(self) -> int:
        if self._payoff_round is None:
            self._payoff_round = random.choice(range(1, C.NUM_ROUNDS + 1))
        return self._payoff_round

    def get_demand(self, randomly: bool = True, player: Optional[BasePlayer] = None) -> float:
        if randomly:
            return round(random.choice(self._demand_rvs))
        else:
            from .models import Player

            assert isinstance(
                player, Player
            ), f'currently, distributions can only be obtained directly from pre-determined data specific to game_number & round_number, which is why player must be provided and be type `models.Player` - additional logic is needed to accommodate a "from-mu-and-sigma" approach as well'

            return TREATMENT_DEMAND_MAP[self.idx][player.game_number - 1][get_round_in_game(player.round_number) - 1]

    def get_demand_rvs(self, size: int = C.RVS_SIZE) -> List[float]:
        """Return samples from the treatment's distribution"""
        distribution = self.get_distribution()
        self._demand_rvs = sample_normal_rvs(distribution.mu, distribution.sigma, size=size)
        return self._demand_rvs

    def get_optimal_order_quantity(self) -> float:
        unit_costs = self.get_unit_costs()
        distribution = self.get_distribution()
        # critical fractile
        critical_fractile = float((unit_costs.rcpu - unit_costs.wcpu) / (unit_costs.rcpu - unit_costs.wcpu + unit_costs.hcpu))
        # critical_demand: inverse CDF at critical fractile
        critical_demand = stats.norm.ppf(critical_fractile)
        return float(distribution.mu + critical_demand * distribution.sigma)

    @staticmethod
    def check_png(png_file: Path) -> bool:
        from datetime import datetime

        return png_file.exists()  # and (datetime.now().timestamp() - png_file.stat().st_mtime) < 86400

    def get_distribution_plot(self, player: Optional[BasePlayer] = None) -> Tuple[Path, Path]:
        """Plot & save the player's current demand distribution data to a png and return the png file path."""

        import matplotlib.pyplot as plt
        import seaborn as sns

        if player:
            from .models import Player

            assert isinstance(player, Player)

        color = "#eb6e08"  # orange-ish

        distribution = self.get_distribution()
        mu, sigma = distribution.mu, distribution.sigma

        png_file = Path(STATIC_DIR).joinpath(f"mu-{mu}-sigma-{sigma:.01f}.png")

        ## TODO(mm): uncomment below to debug appearance of plot in frontend
        # png_file.unlink(missing_ok=True)

        if self.check_png(png_file):
            return png_file

        ## get xmin, xmax
        # data = np.random.normal(mu, sigma, int(1e5))
        # plt.hist(data, bins=100, density=True, alpha=0.6, color="b")
        # xmin, xmax = plt.xlim()
        # plt.close()

        # mean = (xmax + xmin) / 2
        # xmin = mean - 3 * sigma
        # xmax = mean + 3 * sigma

        xmin, xmax = 0, 1000
        # ymax = 0.012 if self.variance_choice == "low" else 0.003

        # make pdf(x)
        x = np.linspace(xmin, xmax, 200)
        p = stats.norm.pdf(x, mu, sigma)

        # plot pdf(x)
        figsize = (5, 4)  # (width, height)
        # figsize = None  # (width, height)
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(x, p, alpha=0.7, color=color)
        ax.fill_between(x, p, 0, alpha=0.2, color=color)

        # plt.xlim((0, xmax))
        # plt.ylim(0, ymax)
        # plt.yticks([])
        # plt.ylabel(None)
        ax.set_xlim((xmin, xmax))
        # ax.set_ylim(0, ymax)
        ax.set_yticks([])
        ax.set_ylabel(None)
        plt.savefig(png_file)

        return png_file


# NOTE: mapping of demand data: keys are treatment indexes, values are Tuple[List[float]], where the tuple has length C.NUM_GAMES & each list has length C.ROUNDS_PER_GAME
TREATMENT_DEMAND_MAP: Dict[int, Tuple[List[float]]] = {
    1: (  # 1: ('low', True)
        [
            495.2006,
            417.4825,
            509.5914,
            597.3164,
            432.8375,
            520.6473,
            566.9467,
            537.0861,
            365.6887,
            622.4456,
            542.5192,
            388.6827,
        ],
        [
            489.539,
            446.6185,
            463.183,
            508.259,
            591.8049,
            499.9106,
            359.4258,
            615.9355,
            433.2883,
            448.2859,
            607.5223,
            539.9545,
        ],
    ),
    2: (  # 2: ('low', False)
        [
            485.7811,
            624.9048,
            511.8574,
            548.9629,
            444.3046,
            484.0875,
            505.3654,
            503.924,
            465.0259,
            453.4967,
            478.7082,
            554.8328,
        ],
        [
            489.539,
            446.6185,
            463.183,
            508.259,
            591.8049,
            499.9106,
            359.4258,
            615.9355,
            433.2883,
            448.2859,
            607.5223,
            539.9545,
        ],
    ),
    3: (  # 3: ('high', True)
        [
            557.9909,
            584.0879,
            316.6598,
            630.902,
            448.9622,
            510.5693,
            348.808,
            557.0162,
            691.8665,
            635.0421,
            612.8592,
            123.6828,
        ],
        [
            359.4258,
            615.9355,
            433.2883,
            448.2859,
            607.5223,
            539.9545,
            653.6855,
            477.2456,
            105.1705,
            518.5136,
            740.276,
            545.8188,
        ],
    ),
    4: (  # 4: ('high', False)
        [
            502.5761,
            565.9565,
            410.3265,
            509.5496,
            384.0769,
            537.0945,
            308.8891,
            668.095,
            519.5882,
            599.8335,
            636.1881,
            370.5609,
        ],
        [
            359.4258,
            615.9355,
            433.2883,
            448.2859,
            607.5223,
            539.9545,
            653.6855,
            477.2456,
            105.1705,
            518.5136,
            740.276,
            545.8188,
        ],
    ),
}
