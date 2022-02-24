import json
from pathlib import Path
from typing import Any, Callable, Optional


def serialize(obj: Any, *args, default: Optional[Callable[[Any], Any]] = None, separators=(",", ":"), **kwargs) -> str:
    """Catch-all handler for object serialization (if no other has been registered via other means)."""
    return json.dumps(obj, *args, default=default, separators=separators, **kwargs)


def get_includable_template_path(template_filepath: str, APP_DIR: Path) -> str:
    """Parse template_filepath to an "includable" template path relative to Path(APP_DIR)."""
    p = Path(template_filepath)
    assert (
        ".html" in p.suffixes
    ), f"""expected template_filepath extension to include {".html"!r} - got {template_filepath!r} (extension {p.suffix!r})."""

    # check first whether template_filepath exists within APP_DIR
    if (APP_DIR / p.name).is_file():
        return str(APP_DIR / p.name)

    else:
        # otherwise, the file is in some other directory

        # ensure the file exists
        (APP_DIR / p).resolve(strict=True)

        # return string for django include expression: {{ include "include_path" }}
        include_path = (APP_DIR / p).relative_to(APP_DIR)
        return str(include_path)
