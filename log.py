#!/usr/bin/env python3

import traceback

class Colors(object):
    class Format(object):
        RESET          = "\033[0m"
        BOLD           = "\033[1m"
        DIM            = "\033[2m"
        UNDERLINED     = "\033[4m"
        BLINK          = "\033[5m"
        REVERSE        = "\033[7m"
        HIDDEN         = "\033[8m"

    class Foreground(object):
        DEFAULT        = "\033[39m"
        BLACK          = "\033[30m"
        RED            = "\033[31m"
        GREEN          = "\033[32m"
        YELLOW         = "\033[33m"
        BLUE           = "\033[34m"
        MAGENTA        = "\033[35m"
        CYAN           = "\033[36m"
        LIGHTGREY      = "\033[37m"
        DARKGREY       = "\033[90m"
        LIGHTRED       = "\033[91m"
        LIGHTGREEN     = "\033[92m"
        LIGHTYELLOW    = "\033[93m"
        LIGHTBLUE      = "\033[94m"
        LIGHTMAGENTA   = "\033[95m"
        LIGHTCYAN      = "\033[96m"
        WHITE          = "\033[97m"
    class Background(object):
        DEFAULT        = "\033[49m"
        BLACK          = "\033[40m"
        RED            = "\033[41m"
        GREEN          = "\033[42m"
        YELLOW         = "\033[43m"
        BLUE           = "\033[44m"
        MAGENTA        = "\033[45m"
        CYAN           = "\033[46m"
        LIGHTGREY      = "\033[47m"
        DARKGREY       = "\033[100m"
        LIGHTRED       = "\033[101m"
        LIGHTGREEN     = "\033[102m"
        LIGHTYELLOW    = "\033[103m"
        LIGHTBLUE      = "\033[104m"
        LIGHTMAGENTA   = "\033[105m"
        LIGHTCYAN      = "\033[106m"
        WHITE          = "\033[107m"

    def __init__(self):
        self.format     = self.Format()
        self.fg         = self.Foreground()
        self.bg         = self.Background()

class Log(object):
    def __init__(self, debug, func=print):
        self.colors = Colors()
        self.debug = debug
        self.func = func

    def construct(self, *args):
        return "".join(args)

    def info(self, msg):
        if self.debug:
            self.func( self.construct( "[", self.colors.fg.LIGHTGREEN, "*", self.colors.fg.DEFAULT, "] ", msg ) )

    def warn(self, msg):
        if self.debug:
            self.func( self.construct( "[", self.colors.fg.LIGHTYELLOW, "!", self.colors.fg.DEFAULT, "] ", msg ) )

    def error(self, msg, exception=None):
        if self.debug:
            self.func( self.construct( "[", self.colors.fg.LIGHTRED, "x", self.colors.fg.DEFAULT, "] ", msg ) )
            if exception:
                self.func( self.construct( "[", self.colors.fg.LIGHTRED, "x", self.colors.fg.DEFAULT, "] ", str(exception) ) )
                traceback.print_tb(exception.__traceback__)
