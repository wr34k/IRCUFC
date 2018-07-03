#!/usr/bin/env python3

class MIRCFormat(object):
    BOLD        = "\x02"
    ITALIC      = "\x1D"
    UNDERLINED  = "\x1F"
    REVERSE     = "\x16"
    RESET       = "\x0F"

    class Colors():
        WHITE       = "00"
        BLACK       = "01"
        BLUE        = "02"
        GREEN       = "03"
        RED         = "04"
        BROWN       = "05"
        PURPLE      = "06"
        ORANGE      = "07"
        YELLOW      = "08"
        LIGHTGREEN  = "09"
        CYAN        = "10"
        LIGHTCYAN   = "11"
        LIGHTBLUE   = "12"
        PINK        = "13"
        GREY        = "14"
        LIGHTGREY   = "15"

    def __init__(self):
        self.colors = self.Colors()

    def color(self, msg, fg, bg=None):
        if bg:
            return "\x03{},{}{}{}".format(fg,bg,msg,self.RESET)
        else:
            return "\x03{}{}{}".format(fg, msg, self.RESET)
