from network import WLAN
from mqtt import MQTTClient
import machine
import time

def settimeout(duration):
    pass

print("Connected to Wifi\n")
client = MQTTClient("demo", "broker.hivemq.com", port=1883)
client.settimeout = settimeout
client.connect()

print ('a')
print (getThermoA())
print ('b')

print (getThermoB())

while True:
     a = getThermoA()
     print("Sending a", a)
     client.publish("/supes/a", str(a))
     time.sleep(2)
     b = getThermoB()
     print("Sending b", b)
     client.publish("/supes/b", str(b))
     time.sleep(2)
