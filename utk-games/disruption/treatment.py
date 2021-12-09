import json
import random
import traceback
from enum import Enum
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

from .constants import NATURAL_MEAN, STATIC_DIR, Constants
from .pydanticmodel import PydanticModel


class UnitCosts(PydanticModel):
    rcpu: Currency  # retail cost / unit (revenue)
    wcpu: Currency  # wholesale cost / unit (order cost)
    hcpu: Currency  # holding cost / unit (stock cost)

    class Config:
        json_encoders = dict(Currency=_CurrencyEncoder)
        arbitrary_types_allowed = True

    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "UnitCosts":
        if treatment.variance_choice == "low":
            rcpu, wcpu, hcpu = [3.00, 1.00, 0.05]
        else:
            rcpu, wcpu, hcpu = [25.00, 14.00, 6.00]
        return UnitCosts(rcpu=rcpu, wcpu=wcpu, hcpu=hcpu)


class DisributionParameters(PydanticModel):
    mu: float
    sigma: float

    @classmethod
    def from_treatment(cls, treatment: "Treatment") -> "DisributionParameters":
        if treatment.variance_choice == "low":
            sigma = 0.067
            # mu, sigma = 6.212, 0.067
        else:
            # mu, sigma = 6.15, 0.35
            sigma = 0.35
        mu = np.log(NATURAL_MEAN) - 0.5 * sigma ** 2

        return DisributionParameters(mu=mu, sigma=sigma)


# TREATMENT_GROUPS = list(product(["high", "low"], [True, False]))
TREATMENT_GROUPS = list(product(["low", "high"], [True, True]))


class Treatment(PydanticModel):
    idx: conint(strict=True, ge=1, le=len(TREATMENT_GROUPS))
    _mu: float = None
    _sigma: float = None
    _payoff_round: int = None
    _demand_rvs: List[float] = []
    _png_file: Path = None
    _disrupted_png_file: Path = None
    _disrupted: bool = False

    class Config:
        extra = Extra.allow

    @property
    def variance_choice(self) -> bool:
        return TREATMENT_GROUPS[self.idx - 1][0]

    @property
    def disruption_choice(self) -> bool:
        return TREATMENT_GROUPS[self.idx - 1][1]

    @classmethod
    def choose(cls) -> "Treatment":
        return Treatment(idx=random.choice(range(len(TREATMENT_GROUPS))) + 1)

    @classmethod
    def from_json(cls, json: StrBytes) -> "Treatment":
        return Treatment.parse_raw(json)

    def is_disrupted(self):
        return self._disrupted

    def get_optimal_order_quantity(self) -> float:
        rcpu, wcpu, hcpu = self.get_unit_costs().tuple()
        cf = float((rcpu - wcpu) / (rcpu - wcpu + hcpu))
        _, sigma = self.get_distribution_parameters().tuple()
        return float(NATURAL_MEAN * np.exp(stats.norm.ppf(cf) * sigma))

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

    def get_demand_rvs(self, size: int = Constants.rvs_size, disrupt: bool = False) -> List[float]:
        """Return samples from the applicable treatment distribution"""

        assert type(size) is int and size > 0, f"""expected size to be a positive integer - got {size}"""

        if len(self._demand_rvs) == size and not disrupt:
            return self._demand_rvs

        mu, sigma = self.get_distribution_parameters().tuple()
        if disrupt:
            self._disrupted = True
            ## transform mu & sigma
            self._mu *= 1
            self._sigma *= 2
        self._demand_rvs = sample_demand_rvs(self._mu, self._sigma, size)
        return self._demand_rvs

    def reset(self):
        size = len(self._demand_rvs) if self._demand_rvs else Constants.rvs_size
        self._mu = None
        self._sigma = None
        self._demand_rvs = []
        _ = self.get_demand_rvs(size=size)
        self._disrupted = False

    def save_distribution_plots(self) -> Tuple[Path, Path]:
        """Returns two file paths: file path of regular disruption plot & file path of disrupted disruption plot."""

        from datetime import datetime

        import matplotlib.pyplot as plt
        import seaborn as sns

        png_file = Path(STATIC_DIR).joinpath(f"distribution-{self.idx}.png")
        disrupted_png_file = Path(STATIC_DIR).joinpath(f"distribution-disrupt-{self.idx}.png")

        if png_file.exists() and (datetime.now().timestamp() - png_file.stat().st_mtime) < 86400:
            self._png_file = png_file

        if disrupted_png_file.exists() and (datetime.now().timestamp() - png_file.stat().st_mtime) < 86400:
            self._disrupted_png_file = disrupted_png_file

        if self._png_file and self._disrupted_png_file:
            return self._png_file, self._disrupted_png_file

        # original props - restore in `finally` block after disrupt
        _mu, _sigma, _demand_rvs = self._mu, self._sigma, self._demand_rvs

        color = "#eb6e08"
        try:
            rvs_regular = self.get_demand_rvs(size=int(1e5))
            rvs_disrupted = self.get_demand_rvs(size=int(1e5), disrupt=True)

            ## get sensible axis limits

            # yaxis max
            sns.displot(rvs_regular, color=color, kind="kde", fill=True)
            ymax_regular = plt.gca().get_ylim()[1]
            plt.cla()
            sns.displot(rvs_disrupted, color=color, kind="kde", fill=True)
            ymax_disrupted = plt.gca().get_ylim()[1]
            plt.cla()
            ymax = max(0.01, ymax_regular, ymax_disrupted)

            # xaxis max
            # xmax = max(rvs_regular + rvs_disrupted)
            xmax = 2000

            # plot regular distribution
            sns.displot(rvs_regular, color=color, kind="kde", fill=True)
            plt.xlim((0, 2000 if xmax > 2000 else xmax))
            plt.ylim(0, ymax)
            plt.yticks([])
            plt.ylabel(None)
            plt.savefig(png_file)

            # plot disrupted distribution
            sns.displot(rvs_disrupted, color=color, kind="kde", fill=True)
            plt.xlim((0, 2000 if xmax > 2000 else xmax))
            plt.ylim(0, ymax)
            plt.yticks([])
            plt.ylabel(None)
            plt.savefig(disrupted_png_file)

            self._png_file, self._disrupted_png_file = png_file, disrupted_png_file
            return self._png_file, self._disrupted_png_file
        finally:
            # reset self params to provided values
            self.reset()


@lru_cache(maxsize=5)
def sample_demand_rvs(mu: float, sigma: float, size: int = int(1e4)) -> List[float]:
    return np.random.lognormal(mu, sigma, size).tolist()
