import machine

# gpio relay
class Relay:
    def __init__(self, gpioPin):
        self.relayPin = gpioPin
        self.relay = machine.Pin(gpioPin, machine.Pin.OUT)

    def setState(self, state):
        self.relay.value(int(state))
        #print ("PIN %s set to %s" % (self.relayPin, int(state)))

    def getState(self):
        return self.relay.value()
