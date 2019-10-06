import os
import datetime
import re
import paho.mqtt.client as mqtt
import secrets
import json

client = mqtt.Client("mqtt_forwarder")
client.username_pw_set(secrets.MQTT_USER, password = secrets.MQTT_PASSWORD)

def on_message(client, userdata, message):
    try:
        print("")
        print("[%s] %s%s:" % (str(datetime.datetime.now()), (message.retain and "{RETAIN} " or ""), message.topic))
        print(
            json.dumps(
                json.loads(
                    message.payload.decode("utf-8")
                ),
                sort_keys=True,
                indent=4
            )
        )
    except Exception as e:
        print(e)

client.on_message = on_message

client.connect(secrets.MQTT_SERVER, port=secrets.MQTT_PORT)

client.subscribe(secrets.MQTT_USER + '/#')

print('Running...')

client.loop_forever()
