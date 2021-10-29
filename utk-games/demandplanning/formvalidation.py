import json
import random
from decimal import ROUND_HALF_UP, Decimal
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

import numpy as np
from otree.api import BasePlayer

# Store registered formfield validator handlers
FORM_FIELD_VALIDATORS: Dict[str, Callable] = {}


def register_formfield_validator(formfield: str):
    assert formfield and type(formfield) is str, f"formfield must be a valid string - got {formfield} ({type(formfield)})"

    def wrapped_validator(validator):
        assert isinstance(validator, Callable), f"validator is not Callable - got {validator} ({type(validator)})"
        FORM_FIELD_VALIDATORS[formfield] = validator
        return validator

    return wrapped_validator


@register_formfield_validator(formfield="ou")
def validate_ou(val: Any) -> None:
    """Validate values for form_field "ou" (order quantity) provided by the client."""

    form_field = "ou"
    expect_type = np.number
    got = val
    got_type = type(val)
    if not isinstance(val, expect_type):
        return {form_field: f"{form_field} (order quantity) is expected to be {expect_type} - got {got} (type: {got_type})"}


def error_message_decorator(error_message_handler) -> Callable:
    """Decorator designed to wrap a custom Page error_message handler to print page form values to console before running
    the handler.
    """
    name = getattr(error_message_handler, "__name__", None)
    if not name == "default_error_message":
        assert (
            name == "error_message"
        ), f"""name of decorated function must be exactly {"error_message"!r} - got name {name} from argument {error_message_handler}"""

    @wraps(error_message_handler)
    def error_message_wrapper(player: BasePlayer, values: Any) -> Optional[Union[dict, str]]:
        """Example ``error_message`` from https://otree.readthedocs.io/en/latest/misc/tips_and_tricks.html#avoid-duplicated-validation-methods:"""
        # print the page's form values to console.
        if values:
            print(f"Page has form values: ", values)
        return error_message_handler(player, values)

    return error_message_wrapper
