import os
import datetime
import re
import paho.mqtt.client as mqtt
import secrets

client = mqtt.Client("mqtt_forwarder")
client.username_pw_set(secrets.MQTT_USER, password = secrets.MQTT_PASSWORD)

clear_all = False

def on_message(client, userdata, message):
    if message.retain:
        print(message.topic)
        if clear_all or input("Clear? [n] ").strip() == "y":
            client.publish(message.topic, "", retain=True)

client.on_message = on_message

client.connect(secrets.MQTT_SERVER)

print('SERVER: %s' % secrets.MQTT_SERVER)
print('USER: %s' % secrets.MQTT_USER)

device = input("DEVICE: ").replace('\n', ' ').replace('\r', '').strip().lower()

if device == "":
    raise Exception("No device provided")

client.subscribe("%s/homeassistant/+/echidna_esp8266_%s/+/config" % (secrets.MQTT_USER, device))

client.subscribe("%s/echidna/esp8266/%s/#" % (secrets.MQTT_USER, device))

print('Running...')

client.loop_forever()
