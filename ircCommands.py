#!/usr/bin/env python3

import time
from fight import Fight

class IrcCommands(object):
    def __init__(self, IRC):
        self.IRC = IRC
        self.fight = Fight(self.IRC)

    def handle_msg(self, chan, admin, nick, user, host, msg):
        args = msg.split()
        if args[0][0] == self.IRC.optkey:
            self.handle_cmd(chan, admin, nick, user, host, args[0][1:], args[1:])


    def check_flood(self, chan, nick):
        if chan not in self.IRC.flood_flag:
            self.IRC.flood_flag[chan] = False
        if chan not in self.IRC.last_cmd:
            self.IRC.last_cmd[chan] = 0

        if self.IRC.flood_flag[chan] and (time.time() - self.IRC.last_cmd[chan]) < 5:
            return True
        if (time.time() - self.IRC.last_cmd[chan]) < 2 and self.IRC.flood_count[chan] > 2:
            self.IRC.privmsg(chan, "{} Slow down m8".format(self.IRC.mirc.color(nick, self.IRC.mirc.colors.RED) ))
            self.IRC.flood_flag[chan]=True
            self.IRC.last_cmd[chan] = time.time()
            return True
        if (time.time() - self.IRC.last_cmd[chan]) < 1:
            self.IRC.flood_count[chan]+=1
            self.IRC.privmsg(chan, "{} Slow down m8".format(self.IRC.mirc.color(nick, self.IRC.mirc.colors.RED) ))
            self.IRC.last_cmd[chan] = time.time()
            return True

        return False



    def handle_cmd(self, chan, admin, nick, user, host, cmd, args):
        if chan == self.IRC.nick:
            chan = nick

        if self.check_flood(chan, nick):
            return

        if admin:
            if cmd == 'raw':
                if args[0].lower() == 'nick':
                    self.IRC.nick = args[1]
                    self.IRC.updateNick()
                elif args[0].lower() == 'join':
                    self.IRC.join(" ".join(args[1:]))
                else:
                    self.IRC.raw(" ".join(args))



        if self.fight.state in ('inactive', 'waiting_fighter'):
            if cmd == 'fight':
                self.fight.addFighter(nick)
                if self.fight.state == 'fighters_ready':
                    self.fight.startFight()

        elif self.fight.state == 'waiting_fighters_action':
            if cmd == 'action':
                if chan != self.IRC.channel:
                    self.fight.set_next_action(nick, args)
                else:
                    self.IRC.privmsg(self.IRC.channel, "{}".format(self.IRC.mirc.color("Not here retard your opponent can see your next move!", self.IRC.mirc.colors.LIGHTRED)))

        else:
            if cmd == 'status':
                self.fight.getStatus(chan)

        self.IRC.flood_flag[chan] = False
        self.IRC.flood_count[chan] = 0
        self.IRC.last_cmd[chan] = time.time()
