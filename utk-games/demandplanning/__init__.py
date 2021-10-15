from os import terminal_size
from pathlib import Path
from string import ascii_uppercase

import pandas as pd
from otree.api import BaseConstants, BaseSubsession, Currency
from otree.session import Session
from rich import print

from . import util
from .models import APP_DIR, Constants, Group, Player, Subsession
from .pages import page_sequence
from .treatment import Treatment

# NOTE: if time, research how to register template function, see `register` in module `otree.templating.nodes`
# from django import template
# register = template.Library()
# @register.simple_tag()
# def addup(*args):
#     ""{% addup 1 2 3 %}""
#     return sum(*args)
