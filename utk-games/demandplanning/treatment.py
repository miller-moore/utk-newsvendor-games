import json
import random
import traceback
from enum import Enum
from itertools import product
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import scipy.stats as stats
from otree.api import BasePlayer, Currency
from otree.currency import _CurrencyEncoder
from pydantic import BaseModel, StrBytes, conint, validator

# NOTE: disruption only applies two first minigame - everybody gets a disruption in the second minigame
VARIABILITY_CHOICES = ["high", "low"]
DISRUPTION_CHOICES = [True, False]
NATURAL_MEAN = 500


class PydanticModel(BaseModel):
    def tuple(self: BaseModel) -> Tuple[Any]:
        """Return a tuple of the pydantic model's attribute values."""
        return tuple(self.dict().values())

    @classmethod
    def from_args(cls, *args, **kwargs) -> "PydanticModel":
        arg_fields = [field_name for field_name in cls.__fields__ if field_name not in kwargs]
        kwargs.update(dict(zip(arg_fields, args)))
        return cls(**kwargs)


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


class Treatment(PydanticModel):
    variance_choice: str
    disruption_choice: bool

    @validator("variance_choice")
    def check_variance_choice(cls, v: Any) -> Any:
        if not v in VARIABILITY_CHOICES:
            raise ValueError(f"""variance_choice must be one of {VARIABILITY_CHOICES!r} - got {v!r} """)
        return v

    @validator("disruption_choice")
    def check_disruption_choice(cls, v: Any) -> Any:
        if not v in DISRUPTION_CHOICES:
            raise ValueError(f"""disruption_choice must be one of {DISRUPTION_CHOICES!r} - got {v!r} """)
        return v

    def has_disruption(self) -> bool:
        return self.disruption_choice

    @classmethod
    def choose(cls) -> "Treatment":
        return TREATMENT_GROUPS[random.choice(list(TREATMENT_GROUPS))]

    @classmethod
    def from_json(cls, json: StrBytes) -> "Treatment":
        return Treatment.parse_raw(json)

    @classmethod
    def from_group_index(cls, index: int) -> "Treatment":
        try:
            return TREATMENT_GROUPS[index]
        except KeyError:
            traceback.print_exc()

    def get_optimal_order_quantity(self) -> float:
        rcpu, wcpu, hcpu = self.get_unit_costs().tuple()
        cf = float((rcpu - wcpu) / (rcpu - wcpu + hcpu))
        _, sigma = self.get_distribution_parameters().tuple()
        return float(NATURAL_MEAN * np.exp(stats.norm.ppf(cf) * sigma))

    def get_unit_costs(self) -> UnitCosts:
        return UnitCosts.from_treatment(self)

    def get_distribution_parameters(self) -> DisributionParameters:
        return DisributionParameters.from_treatment(self)

    def get_demand_rvs(self, size: Optional[int] = None, disrupt: bool = False) -> List[float]:
        """Return samples from the applicable treatment distribution"""

        if size is None:
            size = int(1e4)
        assert type(size) is int and size > 0, f"""expected size to be a positive integer - got {size}"""

        mu, sigma = self.get_distribution_parameters().tuple()
        if disrupt:
            if self.variance_choice == "low":
                # increase sigma
                sigma *= 2
            else:
                # decrease sigma
                sigma /= 2
        return np.random.lognormal(mu, sigma, size).tolist()


TREATMENT_GROUPS = {
    idx + 1: Treatment.from_args(*args) for idx, args in enumerate(product(VARIABILITY_CHOICES, DISRUPTION_CHOICES))
}


def dump_all_treatment_groups(**kwargs) -> str:
    return json.dumps({k: Treatment.from_args(*args).json() for k, args in TREATMENT_GROUPS.items()}, **kwargs)
