from typing import Tuple

from otree.api import Currency
from otree.currency import _CurrencyEncoder
from pydantic import BaseModel


def get_costs(variance_choice: str) -> Tuple[Currency]:
    if variance_choice == "low":
        retail_cost, wholesale_cost, holding_cost = [3.00, 1.00, 0.05]
    else:
        retail_cost, wholesale_cost, holding_cost = [25.00, 14.00, 6.00]
    return Costs(retail_cost=retail_cost, wholesale_cost=wholesale_cost, holding_cost=holding_cost)


class Costs(BaseModel):
    retail_cost: Currency
    wholesale_cost: Currency
    holding_cost: Currency

    class Config:
        json_encoders = dict(Currency=_CurrencyEncoder)
        arbitrary_types_allowed = True
