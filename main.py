from network import WLAN
from mqtt import MQTTClient
from relay import Relay
from thermocouple import Thermocouple
import machine
import time
import json
import uasyncio as asyncio


# wifi config
ssid = "red" #Specify SSID
wifipass = "321123red" # specify wifi password

# mqtt config
mqttbroker = "broker.hivemq.com" # Specify broker DNS name or IP
mqttport = "1883"
mqttuser = ""
mqttpass = ""
mqttprefix = "iot-oven"

# global vars
stateOvenTemp = 25
stateWarmerTemp = 25
stateOven = 0
stateOvenTop = 0
stateGrill = 0
stateLight = 0
stateTargetTemp = 0

# timings
screenUpdateTime = 0.1
tempUpdateTime = 1
controllerUpdateTime = 1

# temp algorythm tuning
tempDamperRange = 10

# init spi comms
spi = machine.SPI(1, baudrate=12500000, sck=machine.Pin(14), miso=machine.Pin(12))

# init uart comms
uart=machine.UART(1,tx=17,rx=16,baudrate=9600)
#uartIRQ = uart.irq(trigger = UART.RX_ANY, priority = 1, handler = irq_fun, wake=machine.IDLE)
end_cmd=b'\xFF\xFF\xFF'


#Define relays and thermocouples - follow same syntax - name: definition
thermos = {
    'thermoMainOven': Thermocouple(gpioPin = 26, spi = spi),
    'thermoWarmerDraw': Thermocouple(gpioPin = 27, spi = spi),
}
elementRelays = {
    96: Relay(gpioPin = 2),  #
    97: Relay(gpioPin = 0),  #
    98: Relay(gpioPin = 15), #
    99: Relay(gpioPin = 4),  #
}


############################
#Lets Go
############################
# connect to wifi
def connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, wifipass) # ssid, password
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
#connect()

def settimeout(duration):
    pass

def send(cmd):
    uart.write(cmd)
    uart.write(end_cmd)
    time.sleep_ms(100)
    a = uart.read()
    print (a)
    return a

# init mqtt
def sub_cb(topic, msg):
    print (type(topic))
    print((topic, msg))

    input = json.loads(msg)
    idx = input['idx']
    nvalue = input['nvalue']
    print ('idx: ' + str(idx))
    print ('nvalue: ' + str(nvalue))
    relay = int(idx)
    print ('relay: ' + str(relay))
    if relay in elementRelays:
        print ("SETTING RELAY TO: " + str(nvalue))
        elementRelays[relay].setState(nvalue)

    """
    tString = topic.decode("utf-8")
    print (type(tString))
    print (tString)
    relay = tString.split('/')[1]
    elementRelays[relay].setState(msg)
    """

"""

client = MQTTClient(mqttuser, mqttbroker, port=mqttport)
client.set_callback(sub_cb)
client.settimeout = settimeout
client.connect()
client.subscribe(b"supes/elementBottom")
client.subscribe(b"supes/elementTop")
client.subscribe(b"domoticz/out")
"""


# reset elementRelays
elementRelays[96].setState(1)
elementRelays[97].setState(1)
elementRelays[98].setState(1)
elementRelays[99].setState(1)


"""
async def sender():
    swriter = asyncio.StreamWriter(uart, {})
    while True:
        print ('s')
        await swriter.awrite('get bGrill.val')
        await swriter.awrite(end_cmd)
        await asyncio.sleep(2)
"""


async def displayChecker():
    global stateOvenTemp, stateWarmerTemp
    global stateOven, stateOvenTop, stateGrill, stateLight, stateTargetTemp
    sreader = asyncio.StreamReader(uart)
    swriter = asyncio.StreamWriter(uart, {})
    while True:
        await swriter.awrite("ovenTemp.val=%s" % (int(stateOvenTemp),))
        await swriter.awrite(end_cmd)
        await swriter.awrite("warmerTemp.val=%s" % (int(stateWarmerTemp),))
        await swriter.awrite(end_cmd)

        await swriter.awrite('get targetTemp.val')
        await swriter.awrite(end_cmd)
        await asyncio.sleep(screenUpdateTime)
        res = await sreader.read()
        if res is not None:
            stateTargetTemp = res[1]

        await swriter.awrite('get bGrill.val')
        await swriter.awrite(end_cmd)
        await asyncio.sleep(screenUpdateTime)
        res = await sreader.read()
        if res is not None:
            stateGrill = res[1]

        await swriter.awrite('get bOven.val')
        await swriter.awrite(end_cmd)
        await asyncio.sleep(screenUpdateTime)
        res = await sreader.read()
        if res is not None:
            stateOven = res[1]

        await swriter.awrite('get bOvenTop.val')
        await swriter.awrite(end_cmd)
        await asyncio.sleep(screenUpdateTime)
        res = await sreader.read()
        if res is not None:
            stateOvenTop = res[1]

        await swriter.awrite('get bLight.val')
        await swriter.awrite(end_cmd)
        await asyncio.sleep(screenUpdateTime)
        res = await sreader.read()
        if res is not None:
            stateLight = res[1]


async def tempChecker():
    global stateOvenTemp, stateWarmerTemp
    global stateOven, stateOvenTop, stateGrill, stateLight, stateTargetTemp

    swriter = asyncio.StreamWriter(uart, {})
    while True:
        await asyncio.sleep(tempUpdateTime)
        stateOvenTemp = thermos['thermoMainOven'].getTemp()
        #print (stateOvenTemp)
        stateWarmerTemp = thermos['thermoWarmerDraw'].getTemp()
        #print (stateWarmerTemp)



async def ovenController():
    global stateOvenTemp, stateWarmerTemp
    global stateOven, stateOvenTop, stateGrill, stateLight, stateTargetTemp
    while True:
        await asyncio.sleep(controllerUpdateTime)
        print ('stateOvenTemp %s stateWarmerTemp %s stateOven %s stateOvenTop %s stateGrill %s stateLight %s stateTargetTemp %s' % (stateOvenTemp, stateWarmerTemp, stateOven, stateOvenTop, stateGrill, stateLight, stateTargetTemp))
        if stateOven == 1:
            #oven is on, lets do stuff
            if stateTargetTemp > stateOvenTemp:
                print ('must warm')
                # set main element to on
                elementRelays[96].setState(0)
                if stateOvenTop == 1:
                    elementRelays[98].setState(0)
                else:
                    elementRelays[98].setState(1)
            else:
                elementRelays[96].setState(1)
                elementRelays[98].setState(1)


        else:
            elementRelays[96].setState(1)
            elementRelays[98].setState(1)


        if stateLight == 1:
            elementRelays[99].setState(0)
        else:
            elementRelays[99].setState(1)



        if stateGrill == 1:
            elementRelays[97].setState(0)
        else:
            elementRelays[97].setState(1)






loop = asyncio.get_event_loop()
#loop.create_task(sender())
loop.create_task(displayChecker())
loop.create_task(tempChecker())
loop.create_task(ovenController())

loop.run_forever()
