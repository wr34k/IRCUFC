#!/usr/bin/env python3

from importlib import reload
import sys

def recompile(modulename):
    try:
        modImport = __import__(modulename)
    except:
        return "Error @ __import__({})".format(modulename)

    pycfile = modImport.__file__

    modPath = pycfile.replace(".pyc", ".py")

    try:
        f = open(modPath, "rU")
        code = f.read()
    except Exception as e:
        return "Error @ open({}, 'rU') : {}".format(modPath, e)

    f.close()

    try:
        compile(code, modulename, "exec")
    except Exception as e:
        return "Error @ compile({}..., {}, 'exec') : {}".format(code[:10], modulename, e)

    try:
        exec(code)
    except Exception as e:
        return "Error @ execfile({}) : {}".format(modPath, e)



    reload(sys.modules[modulename])
    return True


print(recompile("ircCommands"))
