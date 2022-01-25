import itertools
import json
import random
import traceback
from enum import Enum
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import AbstractSet, Any, Callable, Dict, List, Mapping, Optional, Tuple, Union

import numpy as np
import scipy.stats as stats
from otree.api import BasePlayer, Currency
from otree.currency import _CurrencyEncoder
from pydantic import BaseModel, Field, StrBytes, typing, validator
from pydantic.main import Extra
from pydantic.types import confloat, conint

from .constants import STATIC_DIR, C
from .pydanticmodel import PydanticModel
from .util import get_round_in_game

MEANS = [500, 597]
SIGMAS = [50, 100]
UNIT_COSTS = [dict(rcpu=20, wcpu=7.5, scpu=5), dict(rcpu=43, wcpu=6, scpu=5)]

# NOTE: use lru cache to save time when making repeated calls because drawing large samples is slow
@lru_cache(maxsize=10)
def sample_normal_rvs(mu: float, sigma: float, size: int = int(1e4)) -> List[float]:
    return np.random.normal(loc=mu, scale=sigma, size=size).tolist()


class Distribution(PydanticModel):
    mu: float
    sigma: float

    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "Distribution":
        ## NOTE: to convert normal mu/sigma to lognormal mu/sigma, use method of moments: https://en.wikipedia.org/wiki/Log-normal_distribution
        # mu_norm, sigma_norm = TREATMENT_MAP[treatment.idx ][0].tuple()
        # mu = np.log(mu_norm ** 2 / np.sqrt(natural_sigma ** 2 + mu_norm ** 2))
        # sigma = np.sqrt(np.log(natural_sigma ** 2 / (mu_norm ** 2) + 1))
        # return Distribution(mu=mu, sigma=sigma)

        return TREATMENT_MAP[treatment.idx][0]


class UnitCosts(PydanticModel):
    rcpu: Currency  # retail cost per unit
    wcpu: Currency  # wholesale cost per unit
    scpu: Currency  # salvage cost per unit

    class Config:
        json_encoders = dict(Currency=_CurrencyEncoder)
        arbitrary_types_allowed = True

    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "UnitCosts":
        return TREATMENT_MAP[treatment.idx][1]


TREATMENT_MAP: Dict[int, Tuple[Distribution, UnitCosts]] = {
    idx + 1: (Distribution.from_args(mu=mu, sigma=sigma), UnitCosts.from_args(**costs))
    for idx, (mu, sigma, costs) in enumerate(
        [
            (MEANS[0], SIGMAS[1], UNIT_COSTS[0]),
            (MEANS[0], SIGMAS[0], UNIT_COSTS[0]),
            (MEANS[0], SIGMAS[0], UNIT_COSTS[1]),
            (MEANS[0], SIGMAS[1], UNIT_COSTS[1]),
            (MEANS[1], SIGMAS[0], UNIT_COSTS[1]),
            (MEANS[1], SIGMAS[1], UNIT_COSTS[0]),
        ]
    )
}


class Treatment(PydanticModel):
    idx: conint(strict=True, ge=1, le=len(TREATMENT_MAP))
    _demand_rvs: List[float] = []
    _distribution: Distribution = None
    _png_file: Path = None
    _payoff_round: int = None

    class Config:
        extra = Extra.allow

    def reset(self):
        size = len(self._demand_rvs) if self._demand_rvs else C.RVS_SIZE

        self._demand_rvs = self.get_demand_rvs(size=size)
        self._distribution = None
        self._png_file: Path = None
        self._payoff_round: int = None

    @classmethod
    def from_json(cls, json: StrBytes) -> "Treatment":
        return Treatment.parse_raw(json)

    @classmethod
    def choose(cls) -> "Treatment":
        return Treatment(idx=random.choice(list(TREATMENT_MAP)))

    def get_unit_costs(self) -> UnitCosts:
        return UnitCosts.from_treatment(self)

    def get_distribution(self) -> Distribution:
        return Distribution.from_treatment(self)

    def get_payoff_round(self):
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
        overage_cost = unit_costs.wcpu - unit_costs.scpu
        underage_cost = unit_costs.rcpu - unit_costs.wcpu
        # critical fractile
        critical_fractile = float(underage_cost / (underage_cost + overage_cost))
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


## NOTE: mapping of demand data: keys are treatment indexes, values are Tuple[List[float]], where the tuple has length C.NUM_GAMES & each list has length C.ROUNDS_PER_GAME
## NOTE: hardcoded values were first generated as follows before copy/pasting here:
# TREATMENT_DEMAND_MAP: Dict[int, Tuple[List[float]]] = {
#     treatment_idx: tuple(
#         [
#             sample_normal_rvs(mu=distribution.mu, sigma=distribution.sigma, size=C.ROUNDS_PER_GAME)
#             for _ in range(C.NUM_GAMES)
#         ]
#     )
#     for treatment_idx, (distribution, unit_costs) in TREATMENT_MAP.items()
# }

TREATMENT_DEMAND_MAP: Dict[int, Tuple[List[float]]] = {
    1: (
        [
            534.9053318194053,
            670.9203703653983,
            474.37305412386564,
            582.8553459682171,
            378.63474674663183,
            312.63865239812594,
            557.150915396498,
            487.18811232203456,
            613.1403593576564,
            420.3806423206439,
            439.7732574368345,
            678.646620814376,
        ],
    ),
    2: (
        [
            480.7979708723229,
            505.2205827833862,
            516.5768449513579,
            468.2144445938311,
            511.92880376973,
            495.8836552726083,
            439.17885277186355,
            443.454816804914,
            455.80250566977867,
            449.37178314520924,
            527.7373210895437,
            544.0906451940888,
        ],
    ),
    3: (
        [
            480.7979708723229,
            505.2205827833862,
            516.5768449513579,
            468.2144445938311,
            511.92880376973,
            495.8836552726083,
            439.17885277186355,
            443.454816804914,
            455.80250566977867,
            449.37178314520924,
            527.7373210895437,
            544.0906451940888,
        ],
    ),
    4: (
        [
            534.9053318194053,
            670.9203703653983,
            474.37305412386564,
            582.8553459682171,
            378.63474674663183,
            312.63865239812594,
            557.150915396498,
            487.18811232203456,
            613.1403593576564,
            420.3806423206439,
            439.7732574368345,
            678.646620814376,
        ],
    ),
    5: (
        [
            578.3542511859991,
            623.8368862359374,
            546.1051281162959,
            575.8432991364025,
            600.5326327907826,
            559.3172481590334,
            594.5789837381884,
            627.5667667669329,
            564.690783854759,
            596.9277387550078,
            675.9308259578041,
            590.2534937514266,
        ],
    ),
    6: (
        [
            494.29978060608084,
            601.4799478965533,
            530.4062884094968,
            743.5241600073789,
            649.3394450184093,
            570.0086434841705,
            681.6343655109528,
            742.1071899207607,
            450.6687728986678,
            501.96103766254214,
            719.0922973367033,
            554.5020763312828,
        ],
    ),
}
