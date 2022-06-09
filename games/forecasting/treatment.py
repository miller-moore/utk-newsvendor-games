import itertools
import json
import random
import traceback
from decimal import Decimal
from enum import Enum, IntEnum
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import (AbstractSet, Any, Callable, Dict, List, Mapping, Optional,
                    Tuple, Union)

import numpy as np
import scipy.stats as stats
from otree.api import BasePlayer, Currency
from otree.currency import _CurrencyEncoder
from pydantic import (BaseModel, Field, StrBytes, confloat, conint, constr,
                      root_validator, typing, validator)
from pydantic.main import Extra

from .constants import C
from .util import assert_concrete_player, get_round_in_game, is_practice_round

from common.pydanticmodel import PydanticModel  # isort:skip
from common.colors import COLORS  # isort:skip


# NOTE: use lru cache to save time when making repeated calls because drawing large samples is slow
@lru_cache(maxsize=10)
def sample_normal_rvs(mu: float, sigma: float, size: int = int(1e4)) -> List[float]:
    return np.random.normal(loc=mu, scale=sigma, size=size).tolist()


class PracticeTreatmentId(IntEnum):
    ONE = 1  # low costs
    TWO = 2  # high costs


MEANS = [500.0]
SIGMAS = [50.0, 100.0]

PRACTICE_MEAN = 100
PRACTICE_SIGMA = 10


class Distribution(PydanticModel):
    mu: float
    sigma: float

    @validator("mu")
    def validate_mu(cls, v: Any) -> Any:
        if v not in MEANS + [PRACTICE_MEAN]:
            raise ValueError(f"value for mu ({v!r}) is not a member of MEANS ({MEANS!r})")
        return v

    @validator("sigma")
    def validate_sigma(cls, v: Any) -> Any:
        if v not in SIGMAS + [PRACTICE_SIGMA]:
            raise ValueError(f"value for sigma ({v!r}) is not a member of SIGMAS ({SIGMAS!r})")
        return v

    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "Distribution":
        ## NOTE: to convert normal mu/sigma to lognormal mu/sigma, use method of moments: https://en.wikipedia.org/wiki/Log-normal_distribution
        # mu_norm, sigma_norm = TREATMENT_MAP[treatment.id ][0].tuple()
        # mu = np.log(mu_norm ** 2 / np.sqrt(natural_sigma ** 2 + mu_norm ** 2))
        # sigma = np.sqrt(np.log(natural_sigma ** 2 / (mu_norm ** 2) + 1))
        # return Distribution(mu=mu, sigma=sigma)

        return TREATMENT_MAP[treatment.id][0]

    @staticmethod
    def from_practice_treatment_id(cls, practice_treatment_id: PracticeTreatmentId = None) -> "Distribution":
        # return TREATMENT_MAP[practice_treatment_id][0]
        # Note the distribution for practice is a constant (mean: 100, sigma: 10)
        return Distribution(mu=PRACTICE_MEAN, sigma=PRACTICE_SIGMA)


UNIT_COSTS = [
    dict(rcpu=20, wcpu=7.5, scpu=5, category="low"),
    dict(rcpu=43, wcpu=6, scpu=5, category="high"),
]


class UnitCosts(PydanticModel):
    rcpu: Currency  # retail cost per unit
    wcpu: Currency  # wholesale cost per unit
    scpu: Currency  # salvage cost per unit
    category: str  # 'low' or 'high'

    class Config:
        json_encoders = dict(Currency=_CurrencyEncoder)
        arbitrary_types_allowed = True

    @root_validator
    def validate_(cls, values: Any) -> Any:
        if values not in UNIT_COSTS:
            raise ValueError(f"unit costs dictionary ({values!r}) is not a member of UNIT_COSTS ({UNIT_COSTS!r})")
        return values

    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "UnitCosts":
        return TREATMENT_MAP[treatment.id][1]

    @classmethod
    def from_practice_treatment_id(cls, practice_treatment_id: PracticeTreatmentId) -> "UnitCosts":
        return TREATMENT_MAP[practice_treatment_id][1]


class Multiplier(Decimal):
    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "Multiplier":
        return TREATMENT_MAP[treatment.id][2]


class Profitex(Currency):
    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "Profitex":
        return TREATMENT_MAP[treatment.id][3]


class Divisor(Currency):
    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "Divisor":
        return TREATMENT_MAP[treatment.id][4]


TREATMENT_MAP: Dict[int, Tuple[Distribution, UnitCosts, Multiplier, Profitex]] = {
    # 1: (low mean, low var, low costs, multiplier_i, profitex_i)
    1: (
        Distribution(mu=MEANS[0], sigma=SIGMAS[0]),
        UnitCosts.from_args(**UNIT_COSTS[0]),
        Multiplier("0.00080"),
        Profitex(7_000),
        Divisor(1000),
    ),
    # 2: (low mean, high var, high costs, multiplier_i, profitex_i)
    2: (
        Distribution(mu=MEANS[0], sigma=SIGMAS[1]),
        UnitCosts.from_args(**UNIT_COSTS[1]),
        Multiplier("0.00030"),
        Profitex(19_000),
        Divisor(3000),
    ),
}


class Treatment(PydanticModel):
    id: conint(strict=True, ge=1, le=len(TREATMENT_MAP))
    practice_treatment_id: conint(strict=True, ge=1, le=len(PracticeTreatmentId))
    _demand_rvs: List[float] = []
    _disrupted: bool = False
    _distribution: Distribution = None
    _png_file: Path = None
    _payoff_round: int = None

    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True

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
        treatment_id = random.choice(list(TREATMENT_MAP))
        unit_costs: UnitCosts = TREATMENT_MAP[treatment_id][1]
        if unit_costs.category == "high":
            practice_id = PracticeTreatmentId.TWO
        else:
            practice_id = PracticeTreatmentId.ONE
        return Treatment(id=treatment_id, practice_treatment_id=int(practice_id))

    def disrupt(self) -> None:
        # shorthorizon game has no disruptions
        pass

    def is_disrupted(self) -> bool:
        return self._disrupted

    def get_unit_costs(self) -> UnitCosts:
        return UnitCosts.from_treatment(self)

    def get_practice_unit_costs(self) -> UnitCosts:
        return UnitCosts.from_practice_treatment_id(self.practice_treatment_id)

    def get_distribution(self) -> Distribution:
        return Distribution.from_treatment(self)

    def get_practice_distribution(self):
        return Distribution.from_practice_treatment_id(self.practice_treatment_id)

    def get_multiplier(self) -> Multiplier:
        return Multiplier.from_treatment(self)

    def get_profitex(self) -> Profitex:
        return Profitex.from_treatment(self)

    def get_divisor(self) -> Divisor:
        return Divisor.from_treatment(self)

    def get_payoff_round(self):
        if self._payoff_round is None:
            # NOTE: +4 because profit is not computable until the 4th month (round) of the game
            self._payoff_round = random.choice(range(C.PRACTICE_ROUNDS + 4, C.NUM_ROUNDS + 1))

        return self._payoff_round

    def get_payoff(self, player: BasePlayer) -> Currency:
        """
        If the player's current round is equal to their treatment's payoff round,
        then the value returned is the player's payoff, i.e., the result of the calculation:
        >>> Currency(self.get_profitex() * self.get_multiplier())

        Otherwise, Currency(0) is returned.

        Parameters
        ----------
        player : Player
            The player instance is needed to determine whether the player's current round is
            their treatment's originally selected payoff round.

        Returns
        -------
        Currency

        """
        assert_concrete_player(player)
        if player.round_number == player.participant.payoff_round:
            # return Currency(self.get_profitex() * self.get_multiplier())
            return player.profit / self.get_divisor()
        return Currency(0)

    # def get_payoff(self, player: BasePlayer) -> Currency:
    #     """
    #     If the player's current round is equal to their treatment's payoff round,
    #     then the value returned is the player's payoff, i.e., the result of the calculation:
    #     >>> Currency(player.profit * self.get_unit_costs().payoff_factor)

    #     Otherwise, Currency(0) is returned.

    #     Parameters
    #     ----------
    #     player : BasePlayer
    #         The player instance.

    #     Returns
    #     -------
    #     Currency

    #     """
    #     assert_concrete_player(player)
    #     if player.round_number == player.participant.payoff_round:
    #         return Currency(player.profit * self.get_unit_costs().payoff_factor)
    #     return Currency(0)

    def get_demand(self, randomly: bool = True, player: Optional[BasePlayer] = None) -> int:
        if randomly:
            # random selection
            return round(random.choice(self._demand_rvs))
        elif is_practice_round(player.round_number):
            # each practice round has pre-defined demand per round
            practice_demand = {1: 96, 2: 109, 3: 99, 4: 110, 5: 98, 6: 86}
            return practice_demand[player.round_number]
        else:
            from .models import Player

            assert isinstance(
                player, Player
            ), f"currently, demand can only be obtained directly from pre-determined, which depends on Player game_number & round_number and game_number is particular to `models.Player` (not a default field of BasePlayer)"

            game_id = player.game_number - 1
            round_id = get_round_in_game(player.round_number) - 1
            return int(TREATMENT_DEMAND_DATA_MAP[self.id][game_id][round_id])

    def get_demand_rvs(self, size: int = C.RVS_SIZE) -> List[float]:
        """Return samples from the treatment's distribution"""
        distribution = self.get_distribution()
        self._demand_rvs = sample_normal_rvs(distribution.mu, distribution.sigma, size=size)
        return self._demand_rvs

    def get_optimal_order_quantity(self, player: BasePlayer) -> float:
        if is_practice_round(player.round_number):
            unit_costs = self.get_practice_unit_costs()
            distribution = self.get_practice_distribution()
        else:
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
        # from datetime import datetime
        # file_mtime_within_24hours = datetime.now().timestamp() - png_file.stat().st_mtime < 86400

        return png_file.exists()  # and file_mtime_within_24hours

    def get_consent_form_pdf(self) -> Path:
        return Path(C.STATIC_DIR).joinpath("Planner Biases Consent Form- Student Game.pdf")

    def get_instructions_pdf(self) -> Path:
        """
        Return the fully resolved file path (`Path`) of the appropriate instructions manual based on runtime-dependent conditions
        or configuration settings.

        Game instructions depend on the participant's treatment attributes; hence, the file path can only be determined after the
        participant's treatment group is fully constructed. and makes the most sense that the file path be produced by very
        same object which contains participant treatment properties (which is this class, `Treatment`)

        Returns
        -------
        Path

        """
        # if self.get_unit_costs().category == "low":
        #     return Path(C.STATIC_DIR).joinpath(f"GameInstructionsL.pdf")
        # return Path(C.STATIC_DIR).joinpath(f"GameInstructionsH.pdf")
        return Path(C.STATIC_DIR).joinpath(f"GameInstructions.pdf")

    def get_snapshot_instruction_png(self, n: int) -> Path:
        """
        Returns
        -------
        Path

        """
        return Path(C.STATIC_DIR).joinpath(f"snapshot-instructions-{n:d}.png")

    def get_distribution_png(self, practice: bool = False) -> Tuple[Path, Path]:
        """Plot & save the player's current demand distribution data to a png and return the png file path."""

        import matplotlib

        matplotlib.use("agg")
        import matplotlib.pyplot as plt
        import seaborn as sns

        distribution = self.get_practice_distribution() if practice else self.get_distribution()
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

        xmin, xmax = 0, min(1000, 2 * mu)
        # ymax = 0.012 if self.variance_choice == "low" else 0.003

        # make distribution curve
        x = np.linspace(xmin, xmax, 200)
        p = stats.norm.pdf(x, mu, sigma)

        # plot distribution curve
        figsize = (5, 4)  # (width, height)
        # figsize = None  # (width, height)
        fig, ax = plt.subplots(figsize=figsize)
        # ax.plot(x, p, alpha=0.7, color=COLORS["black"])
        ax.fill_between(x, p, 0, alpha=0.5, color=COLORS[color_key])

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


# def generate_treatment_demand_data_map() -> Dict[int, Tuple[List[float], ...]]:
#     return {
#         treatment_id: tuple(
#             [
#                 sample_normal_rvs(mu=distribution.mu, sigma=distribution.sigma, size=C.ROUNDS_PER_GAME)
#                 for _ in range(C.NUM_GAMES)
#             ]
#         )
#         for treatment_id, (distribution, unit_costs) in TREATMENT_MAP.items()
#     }
# TREATMENT_DEMAND_DATA_MAP: Dict[int, Tuple[List[float], ...]] = generate_treatment_demand_data_map()


## NOTE: hardcoded demand data map: keys are treatment indexes, values are Tuple[List[float], ...], where the tuple has length C.NUM_GAMES & each list has length C.ROUNDS_PER_GAME

TREATMENT_DEMAND_DATA_MAP: Dict[int, Tuple[List[float], ...]] = {
    # 1: low mean, low var, low CF
    1: ([440, 520, 570, 539, 582, 528, 485, 441, 486, 440, 502, 483, 545, 434, 518],),
    # 2: low mean, high var, high CF
    2: (
        [445, 505, 530, 450, 742, 443, 417, 496, 437, 501, 628, 544, 608, 444, 357],
    ),
}

