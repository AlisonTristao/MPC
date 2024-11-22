import paho.mqtt.client as mqtt
import time
import random

cliente = mqtt.Client()
cliente.connect('test.mosquitto.org')

while True:
    result = cliente.publish('discretas', random.random())
    print(result)
    time.sleep(1)

cliente.disconnect()