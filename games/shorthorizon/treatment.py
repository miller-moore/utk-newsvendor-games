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

from .constants import C
from .util import get_round_in_game

from common.pydanticmodel import PydanticModel  # isort:skip
from common.colors import COLORS  # isort:skip

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
            (MEANS[0], SIGMAS[1], UNIT_COSTS[0]),  # 1: low mean, high var, low CF
            (MEANS[0], SIGMAS[0], UNIT_COSTS[0]),  # 2: low mean, low var, low CF
            (MEANS[0], SIGMAS[0], UNIT_COSTS[1]),  # 3: low mean, low var, high CF
            (MEANS[0], SIGMAS[1], UNIT_COSTS[1]),  # 4: low mean, high var, high CF
            (MEANS[1], SIGMAS[0], UNIT_COSTS[1]),  # 5: high mean, low var, high CF
            (MEANS[1], SIGMAS[1], UNIT_COSTS[0]),  # 6: high mean, high var, low CF
        ]
    )
}


class Treatment(PydanticModel):
    idx: conint(strict=True, ge=1, le=len(TREATMENT_MAP))
    _demand_rvs: List[float] = []
    _disrupted: bool = False
    _distribution: Distribution = None
    _png_file: Path = None
    _payoff_round: int = None

    class Config:
        extra = Extra.allow

    def reset(self):
        size = len(self._demand_rvs) if self._demand_rvs else C.RVS_SIZE

        self._demand_rvs = self.get_demand_rvs(size=size)
        self._disrupted: bool = False
        self._distribution = None
        self._png_file: Path = None
        self._payoff_round: int = None

    @classmethod
    def from_json(cls, json: StrBytes) -> "Treatment":
        return Treatment.parse_raw(json)

    @classmethod
    def choose(cls) -> "Treatment":
        return Treatment(idx=random.choice(list(TREATMENT_MAP)))

    def disrupt(self) -> None:
        # shorthorizon game has no disruptions
        pass

    def is_disrupted(self) -> bool:
        return self._disrupted

    def get_unit_costs(self) -> UnitCosts:
        return UnitCosts.from_treatment(self)

    def get_distribution(self) -> Distribution:
        return Distribution.from_treatment(self)

    def get_payoff_round(self):
        if self._payoff_round is None:
            self._payoff_round = random.choice(range(1, C.NUM_ROUNDS + 1))

        return self._payoff_round

    def get_demand(self, randomly: bool = True, player: Optional[BasePlayer] = None) -> int:
        if randomly:
            return round(random.choice(self._demand_rvs))
        else:
            from .models import Player

            assert isinstance(
                player, Player
            ), f"currently, demand can only be obtained directly from pre-determined, which depends on Player game_number & round_number and game_number is particular to `models.Player` (not a default field of BasePlayer)"

            game_idx = player.game_number - 1
            round_idx = get_round_in_game(player.round_number) - 1
            return int(TREATMENT_DEMAND_DATA_MAP[self.idx][game_idx][round_idx])

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

    def get_distribution_plot(self) -> Tuple[Path, Path]:
        """Plot & save the player's current demand distribution data to a png and return the png file path."""

        import matplotlib.pyplot as plt
        import seaborn as sns

        distribution = self.get_distribution()
        mu, sigma = distribution.mu, distribution.sigma

        # color_key = "red" if C.APP_NAME == "disruption" and self.is_disrupted() else "ut_orange"
        color_key = "ut_orange"

        png_file = Path(C.STATIC_DIR).joinpath(f"mu-{mu}-sigma-{sigma:.01f}-color-{color_key}.png")

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
        ax.plot(x, p, alpha=1, color=COLORS["ut_smokey"])  # alpha=0.7
        ax.fill_between(x, p, 0, alpha=1, color=COLORS[color_key])  # alpha=0.2

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


def generate_treatment_demand_data_map() -> Dict[int, Tuple[List[float], ...]]:
    return {
        treatment_idx: tuple(
            [
                sample_normal_rvs(mu=distribution.mu, sigma=distribution.sigma, size=C.ROUNDS_PER_GAME)
                for _ in range(C.NUM_GAMES)
            ]
        )
        for treatment_idx, (distribution, unit_costs) in TREATMENT_MAP.items()
    }


# TREATMENT_DEMAND_DATA_MAP: Dict[int, Tuple[List[float], ...]] = generate_treatment_demand_data_map()


## NOTE: hardcoded demand data map: keys are treatment indexes, values are Tuple[List[float], ...], where the tuple has length C.NUM_GAMES & each list has length C.ROUNDS_PER_GAME

TREATMENT_DEMAND_DATA_MAP: Dict[int, Tuple[List[float], ...]] = {
    1: (
        [
            450.2354,
            742.2161,
            442.5504,
            416.9702,
            496.4876,
            436.9613,
            501.2679,
            627.6485,
            544.3831,
            607.5208,
            444.4205,
            356.9525,
        ],
    ),  # 1: low mean, high var, low CF
    2: (
        [538.7785, 581.5469, 528.2913, 485.1264, 441.1537, 486.3506, 440.1492, 502.098, 483.0678, 545.0162, 434.0178, 518.3234],
    ),  # 2: low mean, low var, low CF
    3: (
        [
            450.2354,
            742.2161,
            442.5504,
            416.9702,
            496.4876,
            436.9613,
            501.2679,
            627.6485,
            544.3831,
            607.5208,
            444.4205,
            356.9525,
        ],
    ),  # 3: low mean, low var, high CF
    4: (
        [538.7785, 581.5469, 528.2913, 485.1264, 441.1537, 486.3506, 440.1492, 502.098, 483.0678, 545.0162, 434.0178, 518.3234],
    ),  # 4: low mean, high var, high CF
    5: (
        [650.5515, 582.6913, 611.7078, 583.359, 520.8227, 639.7342, 621.2895, 627.8933, 559.5997, 528.9632, 639.0492, 638.3807],
    ),  # 5: high mean, low var, high CF
    6: (
        [556.5388, 502.2176, 512.5776, 733.732, 575.3298, 530.3528, 599.3154, 477.2013, 749.3481, 729.0584, 666.4436, 527.9543],
    ),  # 6: high mean, high var, low CF
}