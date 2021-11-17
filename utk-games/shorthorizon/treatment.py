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

from .constants import COSTS, MEANS, SIGMAS, STATIC_DIR, Constants
from .pydanticmodel import PydanticModel


class UnitCosts(PydanticModel):
    rcpu: Currency  # retail cost / unit
    wcpu: Currency  # wholesale cost / unit
    scpu: Currency  # salvage cost / unit

    class Config:
        json_encoders = dict(Currency=_CurrencyEncoder)
        arbitrary_types_allowed = True

    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "UnitCosts":
        return TREATMENT_GROUPS[treatment.idx - 1][1]


class DisributionParameters(PydanticModel):
    mu: float
    sigma: float

    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "DisributionParameters":
        ## NOTE: to convert normal to lognormal, use method of moments: https://en.wikipedia.org/wiki/Log-normal_distribution
        # natural_mean, natural_sigma = TREATMENT_GROUPS[treatment.idx - 1][0].tuple()
        # mu = np.log(natural_mean ** 2 / np.sqrt(natural_sigma ** 2 + natural_mean ** 2))
        # sigma = np.sqrt(np.log(natural_sigma ** 2 / (natural_mean ** 2) + 1))
        # return DisributionParameters(mu=mu, sigma=sigma)

        return TREATMENT_GROUPS[treatment.idx - 1][0]


TREATMENT_GROUPS = [
    (DisributionParameters.from_args(mu=mu, sigma=sigma), UnitCosts.from_args(**costs))
    for mu, sigma, costs in itertools.product(MEANS, SIGMAS, COSTS)
]


class Treatment(PydanticModel):
    idx: conint(strict=True, ge=1, le=len(TREATMENT_GROUPS))
    _mu: float = None
    _sigma: float = None
    _payoff_round: int = None
    _demand_rvs: List[float] = []
    _png_file: Path = None

    class Config:
        extra = Extra.allow

    @classmethod
    def choose(cls) -> "Treatment":
        return Treatment(idx=random.choice(range(len(TREATMENT_GROUPS))) + 1)

    @classmethod
    def from_json(cls, json: StrBytes) -> "Treatment":
        return Treatment.parse_raw(json)

    def get_optimal_order_quantity(self) -> float:
        rcpu, wcpu, scpu = self.get_unit_costs().tuple()
        overage_cost = wcpu - scpu
        underage_cost = rcpu - wcpu
        cf = float(underage_cost / (underage_cost + overage_cost))
        mu, sigma = self.get_distribution_parameters().tuple()

        ## NOTE: to convert normal to lognormal, use "Mean" & "Variance" formulas from https://en.wikipedia.org/wiki/Log-normal_distribution
        # natural_mean = np.exp(mu + (1 / 2) * sigma ** 2)
        # natural_sigma = np.sqrt((np.exp(sigma ** 2) - 1) * np.exp(2 * mu + sigma ** 2))
        # return float(natural_mean * np.exp(stats.norm.ppf(cf) * sigma))  # Y = exp(mu + Z * sigma**2), Y~LogNormal

        return float(mu + stats.norm.ppf(cf) * sigma)

    def get_unit_costs(self) -> UnitCosts:
        return UnitCosts.from_treatment(self)

    def get_distribution_parameters(self) -> DisributionParameters:
        if self._mu is None or self._sigma is None:
            self._mu, self._sigma = DisributionParameters.from_treatment(self).tuple()
        return DisributionParameters(mu=self._mu, sigma=self._sigma)

    def get_payoff_round(self):
        if self._payoff_round is None:
            self._payoff_round = random.choice(range(1, Constants.num_rounds + 1))
        return self._payoff_round

    def get_demand_rvs(self, size: int = Constants.rvs_size) -> List[float]:
        """Return samples from the applicable treatment distribution"""
        assert type(size) is int and size > 0, f"""expected size to be a positive integer - got {size}"""

        if len(self._demand_rvs) == size:
            return self._demand_rvs

        if self._mu is None or self._sigma is None:
            _ = self.get_distribution_parameters()
        self._demand_rvs = sample_demand_rvs(self._mu, self._sigma, size)
        return self._demand_rvs

    def reset(self):
        size = len(self._demand_rvs) if self._demand_rvs else Constants.rvs_size
        self._mu = None
        self._sigma = None
        self._demand_rvs = []
        _ = self.get_demand_rvs(size=size)

    def save_distribution_plots(self) -> Path:
        """Returns two file paths: file path of regular disruption plot & file path of disrupted disruption plot."""

        from datetime import datetime

        import matplotlib.pyplot as plt
        import seaborn as sns

        png_file = Path(STATIC_DIR).joinpath(f"distribution-{self.idx}.png")

        if png_file.exists() and not (datetime.now().timestamp() - png_file.stat().st_mtime) >= 86400:
            self._png_file = png_file

        if self._png_file:
            return self._png_file

        # color = "#75e0b0"
        color = "#4daf4a"

        # regular distribution
        rvs = self.get_demand_rvs(size=int(1e5))
        sns.displot(rvs, color=color, kind="kde", fill=True)
        ymax = plt.gca().get_ylim()[1]
        plt.ylim(0, max(0.01, min(ymax, 1)))
        plt.xlim((0, min(2000, max(rvs))))
        plt.ylabel(None)
        plt.savefig(png_file)

        self._png_file = png_file

        return self._png_file


@lru_cache(maxsize=5)
def sample_demand_rvs(mu: float, sigma: float, size: int = int(1e4)) -> List[float]:
    # return np.random.lognormal(mu, sigma, size).tolist()
    return np.random.normal(loc=mu, scale=sigma, size=size).tolist()
