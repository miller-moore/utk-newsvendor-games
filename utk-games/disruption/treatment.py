import json
import random
import traceback
from enum import Enum
from functools import lru_cache
from itertools import product
from typing import AbstractSet, Any, Callable, Dict, List, Mapping, Optional, Tuple, Union

import numpy as np
import scipy.stats as stats
from otree.api import BasePlayer, Currency
from otree.currency import _CurrencyEncoder
from pydantic import BaseModel, Field, StrBytes, typing, validator
from pydantic.main import Extra
from pydantic.types import conint

from .constants import NATURAL_MEAN, Constants

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


TREATMENT_GROUPS = list(product(["high", "low"], [True, False]))
# TREATMENT_GROUPS = list(product(["high", "high"], [True, True]))


class Treatment(PydanticModel):
    idx: conint(strict=True, ge=1, le=len(TREATMENT_GROUPS))
    _mu: float = None
    _sigma: float = None
    _payoff_round: int = None
    _demand_rvs: List[float] = []

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
            ## transform mu & sigma
            self._mu *= 1
            self._sigma *= 2
        self._demand_rvs = generate_demand_rvs(self._mu, self._sigma, size)
        return self._demand_rvs

    def reset(self):
        size = len(self._demand_rvs) if self._demand_rvs else Constants.rvs_size
        self._mu = None
        self._sigma = None
        self._demand_rvs = []
        _ = self.get_demand_rvs(size=size)


@lru_cache(maxsize=5)
def generate_demand_rvs(mu: float, sigma: float, size: int = int(1e4)) -> List[float]:
    return np.random.lognormal(mu, sigma, size).tolist()
