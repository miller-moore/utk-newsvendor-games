import json
import random
from enum import Enum
from itertools import product
from typing import Any, Dict, Optional, Tuple

import numpy as np
from otree.api import Currency
from otree.currency import _CurrencyEncoder
from pydantic import BaseConfig, BaseModel, StrBytes, conint, validator

from .costs import Costs, get_costs

# NOTE: disruption only applies two first minigame - everybody gets a disruption in the second minigame
DISRUPTION_CHOICES = [True, False]
VARIANCE_CHOICES = ["low", "high"]

TREATMENT_COMBINATIONS = list(product(VARIANCE_CHOICES, DISRUPTION_CHOICES))


class Treatment(BaseModel):
    idx: conint(strict=True, ge=1)
    variance_choice: str
    disruption_choice: bool

    @validator("idx")
    def check_idx(cls, v: Any) -> Any:
        validate_treatment_index(v)
        return v

    @validator("variance_choice")
    def check_variance_choice(cls, v: Any) -> Any:
        if not v in VARIANCE_CHOICES:
            raise ValueError(f"""variance_choice must be one of {VARIANCE_CHOICES!r} - got {v!r} """)
        return v

    @validator("disruption_choice")
    def check_disruption_choice(cls, v: Any) -> Any:
        if not v in DISRUPTION_CHOICES:
            raise ValueError(f"""disruption_choice must be one of {DISRUPTION_CHOICES!r} - got {v!r} """)
        return v

    @classmethod
    def choose(cls) -> "Treatment":
        return cls.from_index(random.choice(list(ALL_TREATMENT_GROUPS)))

    @classmethod
    def from_index(cls, treatment_index: int) -> "Treatment":
        validate_treatment_index(treatment_index)

        try:
            return ALL_TREATMENT_GROUPS[treatment_index]
        except KeyError:
            import traceback

            traceback.print_exc()

    @classmethod
    def from_json(cls, json: StrBytes) -> "Treatment":
        return Treatment.parse_raw(json)

    def to_json(self) -> StrBytes:
        return self.json()

    def variance_is_low(self) -> bool:
        return self.variance_choice == "low"

    def disrupt_is_true(self) -> bool:
        return self.disruption_choice

    @property
    def costs(self) -> Costs:
        return get_costs(self.variance_choice)

    @property
    def distribution_params(self) -> Tuple[float]:
        return get_distribution_params(self.variance_choice)

    def rvs(self, size: Optional[int] = None) -> np.ndarray:
        """Return samples from the instance's Lognormal distribution (mu and sigma are set during init)"""

        if size is None:
            size = int(1e4)
        assert type(size) is int and size > 0, f"""expected size to be a positive integer - got {size}"""

        mu, sigma = get_distribution_params(self.variance_choice)
        return np.random.lognormal(mu, sigma, size)


def validate_treatment_index(treatment_index: int):
    if not type(treatment_index) is int and treatment_index in TREATMENT_COMBINATIONS:
        raise ValueError(
            f"""treatment_index must be an integer in range {list(range(1,len(TREATMENT_COMBINATIONS)+1)):!r} (length of TREATMENT_COMBINATIONS)"""
        )


def get_distribution_params(variance_choice: str) -> Tuple[float]:
    Treatment.check_variance_choice(variance_choice)

    if variance_choice == "low":
        mu, sigma = 6.212, 0.067
    else:
        mu, sigma = 6.15, 0.35
    return mu, sigma


def json_dump_all_treatment_groups(**kwargs) -> str:
    return json.dumps({k: v.json() for k, v in ALL_TREATMENT_GROUPS.items()}, **kwargs)


ALL_TREATMENT_GROUPS: Dict[int, Treatment] = {
    idx + 1: Treatment(idx=idx + 1, variance_choice=var_choice, disruption_choice=dis_choice)
    for idx, (var_choice, dis_choice) in enumerate(TREATMENT_COMBINATIONS)
}
