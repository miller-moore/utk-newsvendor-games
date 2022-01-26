from pathlib import Path

from otree.api import BaseConstants, Currency
from otree.constants import BaseConstantsMeta


def get_includable_template_path(app_directory: Path, template_filepath: str) -> str:
    """Parse template_filepath to an "includable" template path, e.g., {{ include "<APP_NAME>/style.html" }} or {{ include C.STYLE_TEMPLATE }}."""
    p = Path(template_filepath)
    assert (
        ".html" in p.suffixes
    ), f"""expected template_filepath extension to include {".html"!r} - got {template_filepath!r} (extension {p.suffix!r})."""

    # strict file path (must exist)
    filepath = (app_directory / template_filepath).resolve(strict=True)

    # return string for django include expression: {{ include "include_path" }}
    include_path = str(Path(app_directory.name) / filepath.name)
    return include_path


# delete `BaseConstantsMeta.__setattr__` to allow customizations to the otree Constants class
# Constants.__setattr__ can be restored to `BaseConstantsMeta__setattr__original` after defining
# the app's Constants class
if hasattr(BaseConstantsMeta, "__setattr__"):
    BaseConstantsMeta__setattr__original = BaseConstantsMeta.__setattr__
    try:
        delattr(BaseConstantsMeta, "__setattr__")
    except:
        pass


class ConstantsBase(BaseConstants, metaclass=BaseConstantsMeta):
    pass
