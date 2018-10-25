from network import WLAN
from mqtt import MQTTClient
from relay import Relay
from thermocouple import Thermocouple
import machine
import time


# connect to wifi
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
connect()


def settimeout(duration):
    pass

# init mqtt
def sub_cb(topic, msg):
    print((topic, msg))
    tString = topic.decode("utf-8")

    print (tString)
    relay = tString.split('/')[1]
    elementRelays[relay].setState(msg)

mqPrefix = 'supes'
client = MQTTClient("demo", "broker.hivemq.com", port=1883)
client.set_callback(sub_cb)
client.settimeout = settimeout
client.connect()
client.subscribe(b"supes/elementBottom")
client.subscribe(b"supes/elementTop")

spi = machine.SPI(1, baudrate=12500000, sck=machine.Pin(14), miso=machine.Pin(12))


# lets setup our components

thermos = {
    'thermoMainOven': Thermocouple(gpioPin = 15, spi = spi),
    'thermoWarmerDraw': Thermocouple(gpioPin = 16, spi = spi),
}

elementRelays = {
    'elementBottom': Relay(gpioPin = 18),
    'elementTop': Relay(gpioPin = 19),
    'elementGrill': Relay(gpioPin = 22),
    'elementWarmer': Relay(gpioPin = 23),
}


# main loop
# todo: make this robust lol
while True:
    time.sleep(1)
    client.check_msg()
    client.publish("/supes/warmer", str(thermos['thermoWarmerDraw'].getTemp()))
    client.publish("/supes/oven", str(thermos['thermoMainOven'].getTemp()))
