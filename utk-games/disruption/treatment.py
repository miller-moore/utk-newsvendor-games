import json
import random
import traceback
from enum import Enum
from itertools import product
from typing import AbstractSet, Any, Callable, Dict, List, Mapping, Optional, Tuple, Union

import numpy as np
import scipy.stats as stats
from otree.api import BasePlayer, Currency
from otree.currency import _CurrencyEncoder
from pydantic import BaseModel, Field, StrBytes, typing, validator
from pydantic.main import Extra

from .constants import DISRUPTION_CHOICES, NATURAL_MEAN, VARIABILITY_CHOICES

IntStr = Union[int, str]
AbstractSetIntStr = AbstractSet[IntStr]
DictIntStrAny = Dict[IntStr, Any]
DictStrAny = Dict[str, Any]
MappingIntStrAny = Mapping[IntStr, Any]


class PydanticModel(BaseModel):
    def tuple(self: BaseModel) -> Tuple[Any]:
        """Return a tuple of the pydantic model's attribute values."""
        return tuple(self.dict().values())

    @classmethod
    def from_args(cls, *args, **kwargs) -> "PydanticModel":
        arg_fields = [field_name for field_name in cls.__fields__ if field_name not in kwargs]
        kwargs.update(dict(zip(arg_fields, args)))
        return cls(**kwargs)

    def __repr_args__(self) -> Any:
        return self.dict().items()

    def dict(
        self,
        *,
        include: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        exclude: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":
        return super().dict(
            include=include or set([c for c in self.__fields__]),
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def json(
        self,
        *,
        include: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        exclude: Union["AbstractSetIntStr", "MappingIntStrAny"] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Optional[Callable[[Any], Any]] = None,
        **dumps_kwargs: Any,
    ) -> str:
        return super().json(
            include=include or set([c for c in self.__fields__]),
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            **dumps_kwargs,
        )


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
    _demand_rvs: List[float] = []

    class Config:
        extra = Extra.allow

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

        if len(self._demand_rvs) == size and not disrupt:
            return self._demand_rvs

        mu, sigma = self.get_distribution_parameters().tuple()
        if disrupt:
            ## transform mu & sigma
            sigma *= 2
            mu *= 1

            ## if transform depends on other things... e.g., variance_choice
            # if self.variance_choice == "low":
            #     sigma *= 2
            #     mu *= 1
            # else:
            #     sigma /= 2
            #     mu *= 1
        self._demand_rvs = np.random.lognormal(mu, sigma, size).tolist()
        return self._demand_rvs


TREATMENT_GROUPS = {
    idx + 1: Treatment.from_args(*args) for idx, args in enumerate(product(VARIABILITY_CHOICES, DISRUPTION_CHOICES))
}

# TREATMENT_GROUPS = {i: Treatment.from_args(*("high", True)) for i in range(1, 5)}


def dump_all_treatment_groups(**kwargs) -> str:
    return json.dumps({k: Treatment.from_args(*args).json() for k, args in TREATMENT_GROUPS.items()}, **kwargs)
