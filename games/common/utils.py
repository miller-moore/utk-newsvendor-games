import json
from typing import Any, Callable, Optional


def serialize(obj: Any, *args, default: Optional[Callable[[Any], Any]] = None, separators=(",", ":"), **kwargs) -> str:
    """Catch-all handler for object serialization (if no other has been registered via other means)."""
    return json.dumps(obj, *args, default=default, separators=separators, **kwargs)
