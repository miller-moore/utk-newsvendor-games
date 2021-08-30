from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import math

author = 'I Leppanen'

doc = """
Drone delivery challenge -- a traveling salesman problem
"""

def moonroverfun(startx,starty,first,second,third,fourth,fifth):

    def distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))

    x =      [9, 8, 8, 7, 7, 7, 5, 2, 1, 4]
    y =      [7, 4, 1, 8, 6, 3, 2, 3, 8, 9] # stratford y coord changed from 10 to 9
    points = [1, 1, 2, 2, 1, 2, 4, 3, 3, 5]
    #sites = ['Plains', 'Boulder', 'Rocks', 'Cliffs', 'Water', 'Life', 'Volcano', 'Mountain', 'Crater', 'Electromagnetic']
    sites = ['Barking','Pier','Shooters Hill','East Ham','Beckton','Woolwich','Greenwich','Millwall','Bow','Stratford']
    ifirst = sites.index(first)
    isecond = sites.index(second)
    ithird = sites.index(third)
    ifourth = sites.index(fourth)
    ififth = sites.index(fifth)

    yourpoints = points[ifirst]

    if isecond is not ifirst:
        yourpoints = yourpoints + points[isecond]

    if ithird is not isecond:
        if ithird is not ifirst:
            yourpoints = yourpoints + points[ithird]

    if ifourth is not ithird:
        if ifourth is not isecond:
            if ifourth is not ifirst:
                yourpoints = yourpoints + points[ifourth]

    if ififth is not ifourth:
        if ififth is not ithird:
            if ififth is not isecond:
                if ififth is not ifirst:
                    yourpoints = yourpoints + points[ififth]

    yourdist = distance(startx,starty,x[ifirst],y[ifirst]) + \
               distance(x[ifirst],y[ifirst],x[isecond],y[isecond]) + \
               distance(x[isecond],y[isecond],x[ithird],y[ithird]) + \
               distance(x[ithird],y[ithird],x[ifourth],y[ifourth]) + \
               distance(x[ifourth],y[ifourth],x[ififth],y[ififth])

    return [yourpoints, yourdist]


class Constants(BaseConstants):
    name_in_url = 'moonrover'
    players_per_group = None
    num_rounds = 20


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    startx = models.IntegerField()
    starty = models.IntegerField()
    firstsite = models.StringField(blank=True)
    secondsite = models.StringField(blank=True)
    thirdsite = models.StringField(blank=True)
    fourthsite = models.StringField(blank=True)
    fifthsite = models.StringField(blank=True)
    points = models.IntegerField(blank=True)
