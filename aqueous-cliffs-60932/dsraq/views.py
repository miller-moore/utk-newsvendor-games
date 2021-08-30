from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class MyPage(Page):
    form_model = models.Player
    form_fields = ['aq1', 'aq2', 'aq3', 'aq4', 'aq5', 'aq6', 'aq7', 'aq8', 'aq9', 'aq10', 'aq11', 'aq12', 'aq13', 'aq14', 'aq15', 'aq16', 'aq17', 'aq18', 'aq19', 'aq20', 'aq21', 'aq22', 'aq23', 'aq24', 'aq25', 'aq26', 'aq27', 'aq28', 'aq29', 'dsr1', 'dsr2', 'dsr3', 'dsr4', 'dsr5', 'dsr6', 'dsr7', 'dsr8', 'dsr9', 'dsr10', 'dsr11', 'dsr12', 'dsr13', 'dsr14', 'dsr15', 'dsr16', 'dsr17', 'dsr18', 'dsr19', 'dsr20', 'dsr21', 'dsr22', 'dsr23', 'dsr24', 'dsr25']

class Results(Page):
    pass


page_sequence = [
    MyPage,
    Results
]
