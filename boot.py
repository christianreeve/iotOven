import array
import machine
import time

def connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('red', '321123red')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


def no_debug():
    import esp
    # this can be run from the REPL as well
    esp.osdebug(None)

def temp_c(data):
    temp = data[0] << 8 | data[1]
    if temp & 0x0001:
        return float('NaN')  # Fault reading data.
    temp >>= 2
    if temp & 0x2000:
        temp -= 16384  # Sign bit set, take 2's compliment.
    return temp * 0.25


def getThermoA():
    cs.value(0)
    t = temp_c(spi.read(2))
    cs.value(1)
    return t

def getThermoB():
    cs2.value(0)
    t = temp_c(spi.read(2))
    cs2.value(1)
    return t


def doTestRun():
    for r in range(0,20):
        time.sleep(0.5)
        a = getThermoA()
        b = getThermoB()
        print ('temp a: %s, temp b: %s' % (a, b))


spi = machine.SPI(1, baudrate=12500000, sck=machine.Pin(14), miso=machine.Pin(12))
cs = machine.Pin(15, machine.Pin.OUT)
cs2 = machine.Pin(16, machine.Pin.OUT)

connect()
machine.main('main.py')
