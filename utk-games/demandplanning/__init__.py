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

# from otree.templating.nodes import Node, gettext, register
# @register('submit_button')
# class SubmitButton(Node):
#     def wrender(self, context):
#         SUBMIT_BTN_TEXT = gettext('Submit')
#         return f'''
#         <p>
#             <button class="otree-btn-next btn btn-primary">{SUBMIT_BTN_TEXT}</button>
#         </p>
#         '''

# from django import template
# register = template.Library()
# @register.simple_tag()
# def addup(*args):
#     ""{% addup 1 2 3 %}""
#     return sum(*args)


print(
    "[blue]TODO[/]: things that need to be in the data card window are described in display_window.html." "\n\n",
)
