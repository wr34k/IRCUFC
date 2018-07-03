#!/usr/bin/python3

import sys, socket, ssl, time, os, re

sys.dont_write_bytecode = True
os.chdir(sys.path[0] or ".")
sys.path += ("..", "../IRCUFC")

import ircEvents

from log import Colors, Log
from mircformat import MIRCFormat
from ircReload import recompile
from ircCommands import IrcCommands


server     = 'irc.underworld.no'
port       = 9999
channel   = ('#IRCUFC', None) # (chan, key)
use_ssl    = True

nickname = 'IRCUFC'
username = 'McBuffer'
realname = '** WE FIGHTIN **'

optkey= "!"

DEBUG = True


class IrcBot(object):

    def __init__(self):
        self.sock           = None
        self.lag            = False

        self.last_cmd       = {}
        self.flood_flag     = {}
        self.flood_count    = {}
        self.timeouts       = {}

        self.mirc           = MIRCFormat()
        self.log            = Log(DEBUG)
        self.cmds           = IrcCommands(self)

        self.server         = server
        self.port           = port
        self.ssl            = use_ssl

        self.nick           = nickname
        self.user           = username
        self.real           = realname

        self.optkey         = optkey

        self.channel,self.chankey = channel


    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if use_ssl:
                self.sock = ssl.wrap_socket(self.sock)
            self.sock.connect((server, port))
        except Exception as e:
            self.log.error("Connexion failed", e)
            return


    def run(self):
        self.connect()
        self.register()
        self.listen()

    def register(self):
        self.raw("USER {} 0 * :{}".format(self.user, self.real))
        self.raw("NICK {}".format(self.nick))

    def updateNick(self):
        self.raw("NICK {}".format(self.nick))

    def listen(self):
        while True:
            try:
                if self.lag:
                    self.lag=False
                    data += self.sock.recv(1024).decode('utf-8', 'ignore')
                else:
                    data = self.sock.recv(1024).decode('utf-8', 'ignore')

                for line in [x.split() for x in data.split("\r\n") if len(x.split()) > 1]:
                    self.log.info("<< {}".format(' '.join(line)))

                    if line[0][1:] == 'ING':
                        ircEvents.eventPING(self, line)

                    else:
                        try:
                            getattr(ircEvents, "event{}".format(line[1].upper()))(self, line)
                        except:
                            pass

            except (UnicodeDecodeError, UnicodeEncodeError):
                pass

            except KeyboardInterrupt:
                self.log.warn("^C, Exiting...")
                return

            except Exception as e:
                self.log.error("Exception in listen()", e)
                pass

    def join(self):
        self.raw("JOIN {} {}".format(self.channel, self.chankey)) if self.chankey else self.raw("JOIN {}".format(self.channel))


    def raw(self, msg, timeout=None):
        msg = msg.replace("\r", "")
        msg = msg.replace("\n", "")
        self.log.info(">> " + msg)
        self.sock.send(bytes(msg + "\r\n", 'utf-8'))
        if timeout:
            time.sleep(timeout)

    def isAdmin(self, ident):
        ret = False
        for line in [line.strip() for line in open('assets/admins', 'r').readlines() if line]:
            if re.compile(line.replace('*', '.*')).search(ident):
                ret = True
        return ret


    def handle_msg(self, chan, admin, nick, user, host, msg):
        args = msg.split()
        if admin:
            if args[0] == '{}reload'.format(self.optkey):
                ret = recompile(args[1]) # Let you add new code to the bot without restarting it
                if ret == True:
                    self.privmsg(chan, "{} recompiled successfully!".format(self.mirc.color(args[1], self.mirc.colors.GREEN)))
                    return
                else:
                    self.privmsg(chan, "Man we had a issue while recompiling {}".format(self.mirc.color(args[1], self.mirc.colors.GREEN)))
                    self.log.error(ret)
                    return

        self.cmds.handle_msg(chan, admin, nick, user, host, msg)


    def privmsg(self, chan, msg):
        if chan not in self.timeouts:
            self.timeouts[chan] = {'last_cmd': time.time(), 'burst': 0, 'timeout': 0}
        self.raw("PRIVMSG {} :{}".format(chan, msg), self.timeouts[chan]['timeout'])
        self.editTimeouts(chan)



    def editTimeouts(self, chan):
        if (time.time() - self.timeouts[chan]['last_cmd']) < 3:
            self.timeouts[chan]['burst'] += 1
        else:
            self.timeouts[chan]['burst'] = 0

        if self.timeouts[chan]['burst'] > 3:
            self.timeouts[chan]['timeout'] += 0.075
        else:
            self.timeouts[chan]['timeout'] = 0

        if self.timeouts[chan]['timeout'] > 0.4:
            self.timeouts[chan]['timeout'] = 0.4

        self.timeouts[chan]['last_cmd'] = time.time()


    def action(self, chan, msg):
        self.privmsg(chan, "\x01ACTION {}\x01".format(msg))
