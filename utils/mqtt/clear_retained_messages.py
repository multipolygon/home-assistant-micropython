import os
import datetime
import re
import paho.mqtt.client as mqtt
import secrets

client = mqtt.Client("mqtt_forwarder")
client.username_pw_set(secrets.MQTT_USER, password = secrets.MQTT_PASSWORD)

def on_message(client, userdata, message):
    if message.retain:
        print(message.topic)
        if input("Clear? [n] ").strip() == "y":
            client.publish(message.topic, "", retain=True)

client.on_message = on_message

client.connect(secrets.MQTT_SERVER, port=secrets.MQTT_PORT)

topic = input("\nTopic? [%s] " % secrets.MQTT_USER).replace('\n', ' ').replace('\r', '').strip()

if topic == "":
    raise Exception("No topic provided")

client.subscribe(topic)

print('Running...')

client.loop_forever()
