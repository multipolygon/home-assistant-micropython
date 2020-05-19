import os
import datetime
import re
import paho.mqtt.client as mqtt
import json
from argparse import ArgumentParser

def args():
    p = ArgumentParser()
    p.add_argument("--secrets", '-s', action="store", type=str, help='Transfer specified file as secrets.json')
    return p.parse_args()

args = args()

with open(args.secrets) as f:
    secrets = json.loads(f.read())

client = mqtt.Client("mqtt_forwarder")
client.username_pw_set(secrets['MQTT_USER'], password = secrets['MQTT_PASSWORD'])

def on_message(client, userdata, message):
    try:
        print("")
        print("[%s] %s%s:" % (str(datetime.datetime.now()), (message.retain and "{RETAIN} " or ""), message.topic))
        text = message.payload.decode("utf-8")
        try:
            print(
                json.dumps(
                    json.loads(
                        text
                    ),
                    sort_keys=True,
                    indent=4
                )
            )
        except:
            print(text)
    except Exception as e:
        print(e)

client.on_message = on_message

client.connect(secrets['MQTT_SERVER'])

client.subscribe(secrets['MQTT_PREFIX'] + '/#')

print('Running...')

client.loop_forever()
