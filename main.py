
import os, sys

sys.dont_write_bytecode = True
os.chdir(sys.path[0] or ".")
sys.path += ("irc", "IRCUFC")


if __name__ == '__main__':
    import irc
    irc.IrcBot().run()
