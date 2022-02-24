# See https://otree.readthedocs.io/en/latest/misc/otreelite.html?highlight=filter#templates
from typing import Iterable

from otree.templating import filters


@filters.register("type")
def _type(value):
    return type(value)


@filters.register("len")
def _len(value):
    try:
        return len(value)
    except:
        return 0 if not value else 1


@filters.register
def isiterable(value):
    return isinstance(value, Iterable)


@filters.register
def add(value, other=0):
    try:
        if int(value) == value and int(other) == other:
            return int(value + other)
    except:
        pass
    try:
        return float(value) + float(other)
    except:
        pass
    try:
        return value + other
    except:
        pass
    return ""


@filters.register
def mul(value, other=0):
    try:
        if int(value) == value and int(other) == other:
            return int(value * other)
    except:
        pass
    try:
        return float(value) * float(other)
    except:
        pass
    try:
        return value * other
    except:
        pass
    return ""
