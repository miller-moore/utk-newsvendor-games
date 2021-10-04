import random
from enum import Enum
from itertools import product


class EnumBase(Enum):
    @classmethod
    def members(cls):
        return list(cls.__members__.values())


class VarianceOption(EnumBase):
    LOW = 0
    HIGH = 1


class DisruptionOption(EnumBase):
    FALSE = 0
    TRUE = 1


class TreatmentGroup(object):
    def __init__(self, variance_option: VarianceOption, disruption_option: DisruptionOption):
        self.variance_option = variance_option
        self.disruption_option = disruption_option

    def variance_is_low(self) -> bool:
        return self.variance_option is VarianceOption.LOW

    def variance_is_high(self) -> bool:
        return not self.variance_is_low()

    def disruption_is_true(self) -> bool:
        return self.disruption_option is DisruptionOption.TRUE

    def disruption_is_false(self) -> bool:
        return not self.disruption_is_true()


TREATMENT_GROUPS = [TreatmentGroup(*options) for options in product(VarianceOption.members(), DisruptionOption.members())]


def select_random_treatment_group() -> TreatmentGroup:
    return random.choice(TREATMENT_GROUPS)
