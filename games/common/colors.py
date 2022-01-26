from .pydanticmodel import PydanticModel


class Colors(PydanticModel):
    black: str = "#000000"
    blue: str = "#377eb8"
    cyan: str = "#60d3eb"
    darkblue: str = "#6160eb"
    darkgreen: str = "#006f60"
    darkmango: str = "#eb6e08"
    darkpink: str = "#aa3382"
    facebook: str = "#3b5998"
    green: str = "#4daf4a"
    lightgreen: str = "#75e0b0"
    mango: str = "#ffbf34"
    orange: str = "#eeac4d"
    pink: str = "#ff56c6"
    purple: str = "#6f3098"
    red: str = "#f12761"
    ut_orange: str = "#FF8200"
    ut_smokey: str = "#58595B"


COLORS = Colors().dict()
