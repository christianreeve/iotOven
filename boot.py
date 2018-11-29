import array
import machine
import time



def no_debug():
    import esp
    # this can be run from the REPL as well
    esp.osdebug(None)


machine.main('main.py')
