from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class MyPage(Page):
    form_model = models.Player
    form_fields = ['name', 'email',
                   'q1a', 'q1b',
                   'q2a', 'q2b',
                   'q3a', 'q3b',
                   'q4a', 'q4b',
                   'q5a', 'q5b',
                   'q6a', 'q6b',
                   'q7a', 'q7b',
                   'q8a', 'q8b',
                   'q9a', 'q9b',
                   'q10a', 'q10b',
                   'q11a', 'q11b',
                   'q12a', 'q12b',
                   'q13a', 'q13b',
                   'q14a', 'q14b',
                   'q15a', 'q15b',
                   'q16a', 'q16b',
                   'q17a', 'q17b',
                   'q18a', 'q18b',
                   'q19a', 'q19b',
                   'q20a', 'q20b',
                   'q21a', 'q21b',
                   'q22a', 'q22b',
                   'q23a', 'q23b',
                   'q24a', 'q24b',
                   'q25a', 'q25b',
                   'q26a', 'q26b',
                   'q27a', 'q27b',
                   'q28a', 'q28b',
                   'q29a', 'q29b',
                   'q30a', 'q30b',
                   'qq1a', 'qq1b', 'qq1c', 'qq1d',
                   'qq2a', 'qq2b', 'qq2c', 'qq2d',
                   'qq3a', 'qq3b', 'qq3c', 'qq3d',
                   'qq4a', 'qq4b', 'qq4c', 'qq4d',
                   'qq5a', 'qq5b', 'qq5c', 'qq5d',
                   'qq6a', 'qq6b', 'qq6c', 'qq6d',
                   'qq7a', 'qq7b', 'qq7c', 'qq7d',
                   'qq8a', 'qq8b', 'qq8c', 'qq8d',
                   'qq9a', 'qq9b', 'qq9c', 'qq9d',
                   'qq10a', 'qq10b', 'qq10c', 'qq10d',
                   'qq11a', 'qq11b', 'qq11c', 'qq11d',
                   'qq12a', 'qq12b', 'qq12c', 'qq12d',
                   'qq13a', 'qq13b', 'qq13c', 'qq13d',
                   'qq14a', 'qq14b', 'qq14c', 'qq14d',
                   'qq15a', 'qq15b', 'qq15c', 'qq15d'
                   ]


class Results(Page):
    pass


page_sequence = [
    MyPage
]
