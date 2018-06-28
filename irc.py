#!/usr/bin/python3

import sys, socket, ssl, time, os, re

from log import Colors, Log
from mircformat import MIRCFormat
from ircReload import recompile

from ircCommands import IrcCommands


server     = 'irc.servercentral.net'
port       = 9999
channel   = ('#IRCUFC', None) # (chan, key)
use_ssl    = True

nickname = 'IRCUFC'
username = 'McBuffer'
realname = '** WE FIGHTIN **'

optkey= "!"
timeout=0.4

DEBUG = True
sys.dont_write_bytecode = True


class Irc(object):

    def __init__(self):
        self.sock = None
        self.lag=False

        self.last_cmd={}
        self.flood_flag={}
        self.flood_count={}

        self.mirc = MIRCFormat()

        self.optkey = optkey

        self.log = Log(DEBUG)

        self.server = server
        self.port = port
        self.ssl = use_ssl

        self.nick = nickname
        self.user = username
        self.real = realname

        self.channel, self.chankey = channel

        self.nameslists = {}
        self.nameslistFlag = {}

        self.cmds = IrcCommands(self)

        self.timeouts = {}

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
        self.log.info("Identifying...")
        self.raw("USER {} 0 * :{}".format(self.user, self.real))
        self.raw("NICK {}".format(self.nick))

    def updateNick(self):
        self.log.info("Updating NICK to {}".format(self.nick))
        self.raw("NICK {}".format(self.nick))

    def listen(self):
        while True:
            if self.lag:
                self.lag=False
                data += self.sock.recv(1024).decode('utf-8', 'ignore')
            else:
                data = self.sock.recv(1024).decode('utf-8', 'ignore')

            for line in [x.split() for x in data.split("\r\n") if len(x.split()) > 1]:
                self.log.info("<< {}".format(' '.join(line)))

                if line[0][1:] == 'ING':
                    self.raw("PONG {}".format(line[1]))

                elif line[1] == '001': # connected
                    self.join()

                elif line[1] == 'JOIN': # Someone joined a channel
                    self.log.info("{} JOIN to {}".format(line[0], line[2]))
                    pass

                elif line[1] == 'PART': # Someone emopart a channel
                    self.log.info("{} PART from {}".format(line[0], line[2]))
                    pass

                elif line[1] == '433': # Nick already in use
                    self.nick += "_"
                    self.updateNick()

                elif line[1] == 'KICK': #Got kicked lmao
                    if line[0][1:].split("@")[0].split("!") == self.nick:
                        self.log.warn("Got kicked from {} !".format(line[2]))
                        chan = line[2]
                        if chan == self.channel:
                                self.join()

                elif line[1] == 'INVITE':
                    self.log.info("{} invited the bot to {}".format(line[0][1:].split("!")[0], line[3][1:]))
                    self.join(line[3][1:])


                elif line[1] == 'PRIVMSG':
                    nick,user   = line[0][1:].split("@")[0].split("!")
                    user = user[1:] if user[0] == '~' else user
                    host        = line[0].split("@")[1]
                    self.handle_msg(line[2], self.isAdmin(line[0][1:]), nick, user, host, ' '.join(line[3:])[1:])

    def join(self):
        self.log.info("Now joining {} ...".format(self.channel))
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
        for line in [line.strip() for line in open('admins', 'r').readlines() if line]:
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


if __name__=='__main__':
    Irc().run()
