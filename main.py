
import os, sys

sys.dont_write_bytecode = True
os.chdir(sys.path[0] or ".")
sys.path += ("irc", "IRCUFC")

server     = 'irc.arabs.ps'
port       = 6697
channel   = ('#IRCUFC', None) # (chan, key)
use_ssl    = True

nickname = 'IRCUFC'
username = 'McBuffer'
realname = '** WE FIGHTIN **'

optkey= "!"

DEBUG = True

if __name__ == '__main__':
    import irc
    irc.IrcBot(nickname, username, realname, server, port, use_ssl, channel, optkey, DEBUG).init()
