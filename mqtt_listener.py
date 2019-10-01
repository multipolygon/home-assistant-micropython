import os
import datetime
import re
import paho.mqtt.client as mqtt
import secrets

client = mqtt.Client("mqtt_forwarder")
client.username_pw_set(secrets.MQTT_USER, password = secrets.MQTT_PASSWORD)

def on_message(client, userdata, message):
    print("[%s] %s: %s" % (str(datetime.datetime.now()), message.topic, message.payload.decode("utf-8")))

client.on_message = on_message

client.connect(secrets.MQTT_SERVER, port=secrets.MQTT_PORT)

client.subscribe('#')

print('Running...')

client.loop_forever()
