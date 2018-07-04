#!/usr/bin/env python3

import time

def eventPING(IRC, line):
    IRC.queue("PONG {}".format(line[1]))

def event001(IRC, line):
    IRC.join()

def event433(IRC, line):
    IRC.nick += "_"
    IRC.updateNick()

def eventJOIN(IRC, line):
    IRC.log.info("{} JOIN to {}".format(line[0], line[2]))

def eventPART(IRC, line):
    IRC.log.info("{} PART from {}".format(line[0], line[2]))

def eventKICK(IRC, line):
    if line[3] == IRC.nick:
        IRC.log.warn("Got kicked from {} !".format(line[2]))
        chan = line[2]
        if chan == IRC.channel:
            IRC.join()

def eventQUIT(IRC, line):
    if line[0][1:].split("@")[0].split("!")[0] == IRC.nick:
        IRC.log.warn("quit ! Reconnecting in 15 seconds..")
        time.sleep(15)
        IRC.init()

def eventINVITE(IRC, line):
    IRC.log.info("{} invited the bot to {}".format(line[0][1:].split("!")[0], line[3][1:]))

def eventPRIVMSG(IRC, line):
    nick,user   = line[0][1:].split("@")[0].split("!")
    user        = user[1:] if user[0] == '~' else user
    host        = line[0].split("@")[1]
    try:
        IRC.handle_msg(line[2], IRC.isAdmin(line[0][1:]), nick, user, host, ' '.join(line[3:])[1:])
    except:
        pass
