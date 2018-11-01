import machine

# gpio relay
class Thermocouple:
    def __init__(self, spi, gpioPin):
        self.spi = spi
        self.cs = machine.Pin(gpioPin, machine.Pin.OUT)
        self.csPin = gpioPin

    def temp_c(self,data):
        print ('converting raw data: ', data)
        temp = data[0] << 8 | data[1]
        if temp & 0x0001:
            return float('NaN')  # Fault reading data.
        temp >>= 2
        if temp & 0x2000:
            temp -= 16384  # Sign bit set, take 2's compliment.
        return temp * 0.25

    def getTemp(self):
        self.cs.value(0)
        t = self.temp_c(self.spi.read(2))
        self.cs.value(1)
        print ("Read thermo PIN %s" % (self.csPin,))
        return t
