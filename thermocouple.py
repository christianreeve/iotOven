import machine

# gpio relay
class Thermocouple:

    def __init__(self, spi, gpioPin):
        self.spi = spi
        self.cs = machine.Pin(gpioPin, machine.Pin.OUT)
        self.csPin = gpioPin
    #
    # def toBinary(self, n):
    #     return ''.join(str(1 & int(n) >> i) for i in range(16)[::-1])
    #
    # def temp_c(self,data):
    #     print (data)
    #     s = self.toBinary(data)
    #     f = int(s[1:13],2)
    #     print (f)
    #     return f
    # #
    # def getTemp(self):
    #     self.cs.value(0)
    #     r = self.spi.read(2)
    #     print (r)
    #     t = self.temp_c(r)
    #
    #     self.cs.value(1)
    #     print ("Read thermo PIN %s" % (self.csPin,))
    #     return t

    def getTemp(self):
        """Return the thermocouple temperature value in degrees celsius."""
        v = self._read16()
        # Check for error reading value.
        if v & 0x4:
            return float('NaN')
        # Check if signed bit is set.
        if v & 0x80000000:
            # Negative value, take 2's compliment. Compute this with subtraction
            # because python is a little odd about handling signed/unsigned.
            v >>= 3 # only need the 12 MSB
            v -= 4096
        else:
            # Positive value, just shift the bits to get the value.
            v >>= 3 # only need the 12 MSB
        return v * 0.25

    def _read16(self):
        self.cs.value(0)
        raw = self.spi.read(2)
        self.cs.value(1)
        if raw is None or len(raw) != 2:
            raise RuntimeError('Did not read expected number of bytes from device!')
        value = raw[0] << 8 | raw[1]
        return value
