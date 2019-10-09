import os
import datetime
import re
import paho.mqtt.client as mqtt
import secrets

if input("\nErase all retained messages? (type yes) ").strip() == "yes":
    client = mqtt.Client("mqtt_forwarder")
    client.username_pw_set(secrets.MQTT_USER, password = secrets.MQTT_PASSWORD)

    def on_message(client, userdata, message):
        if message.retain:
            print(message.topic)
            client.publish(message.topic, "", retain=True)

    client.on_message = on_message

    client.connect(secrets.MQTT_SERVER, port=secrets.MQTT_PORT)

    client.subscribe(secrets.MQTT_USER + '/#')

    print('Running...')

    client.loop_forever()
