"""
https://otree.readthedocs.io/en/latest/forms.html#error-message
https://otree.readthedocs.io/en/latest/misc/tips_and_tricks.html#duplicate-validation-methods
"""

import json
import random
from decimal import ROUND_HALF_UP, Decimal
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

import numpy as np
from otree.api import BasePlayer
from otree.models import Participant

# Store registered form_field validator handlers
FORM_FIELD_VALIDATORS: Dict[str, Callable] = {}


def register_form_field_validator(
    form_field: str,
    expect_type: Type,
):
    assert form_field and type(form_field) is str, f"form_field must be a valid string - got {form_field} ({type(form_field)})"
    assert type(expect_type) is type, f"""expect_type must be type - got {expect_type} (type: {type(expect_type)})"""

    def wrapper(validator: Callable):
        assert isinstance(validator, Callable), f"validator argument is not Callable: {validator!r} ({type(validator)})"

        @wraps(validator)
        def wrapped_validator(*args, **kwargs):
            val = args[0] if args else kwargs.get(form_field, None)
            if type(val) is not expect_type:
                return f"Expected {expect_type!r} for form field {form_field!r} (got {type(val)})."
            return validator(val)

        FORM_FIELD_VALIDATORS[form_field] = wrapped_validator
        return validator

    return wrapper


def error_message_decorator(error_message_handler) -> Callable:
    """Decorator designed to wrap a custom Page error_message handler to print page form values to console before running
    the handler.
    """
    from .util import get_page_name

    name = getattr(error_message_handler, "__name__", None)
    if not name == "default_error_message":
        assert (
            name == "error_message"
        ), f"""name of decorated function must be exactly {"error_message"!r} - got name {name} from argument {error_message_handler}"""

    @wraps(error_message_handler)
    def error_message_wrapper(player: BasePlayer, values: Any) -> Optional[str]:
        """Example ``error_message`` from https://otree.readthedocs.io/en/latest/misc/tips_and_tricks.html#avoid-duplicated-validation-methods:"""
        # print the page's form values to console.
        if values:
            print(
                f"error_message_decorator: Round {player.round_number}: {get_page_name(player)} Page has form values: {values!r}"
            )
        return error_message_handler(player, values)

    return error_message_wrapper


@error_message_decorator
def default_error_message(player: BasePlayer, values: Any):

    if not type(values) is dict:
        return

    error_messages = dict()
    for field in values:
        if field in FORM_FIELD_VALIDATORS:
            validator = FORM_FIELD_VALIDATORS[field]
            try:
                msg = validator(values[field])
                if type(msg) is str:
                    error_messages[field] = msg
            except Exception as e:
                error_messages[field] = str(e)
    return error_messages
