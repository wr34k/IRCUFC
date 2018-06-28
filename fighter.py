#!/usr/bin/env python3




class Fighter(object):
    def __init__(self, nick, colour):

        self.nick = nick
        self.colour = colour

        self.hp = 100
        self.stance = 'stand'

        self.nextAction = None

        self.advantage = False
        self.groundpos = None

        self.first_time_lowhp = True

        self.wins = 0
        self.looses = 0
