import os
import datetime
import re
import paho.mqtt.client as mqtt
import json
from argparse import ArgumentParser

def args():
    p = ArgumentParser()
    p.add_argument("--secrets", '-s', action="store", type=str, help='Transfer specified file as secrets.json')
    p.add_argument("--all", action="store_true", help="Clear all.")
    return p.parse_args()

args = args()

with open(args.secrets) as f:
    secrets = json.loads(f.read())

client = mqtt.Client("mqtt_forwarder")
client.username_pw_set(secrets['MQTT_USER'], password = secrets['MQTT_PASSWORD'])

def on_message(client, userdata, message):
    if message.retain:
        print(message.topic)
        if args.all or input("Clear? [n] ").strip() == "y":
            client.publish(message.topic, "", retain=True)

client.on_message = on_message

client.connect(secrets['MQTT_SERVER'])

print('SERVER: %s' % secrets['MQTT_SERVER'])
print('USER: %s' % secrets['MQTT_USER'])

client.subscribe("#")

print('Running...')

client.loop_forever()
