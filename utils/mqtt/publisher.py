import os
import paho.mqtt.client as mqtt
import secrets

client = mqtt.Client("mqtt_publisher")
client.username_pw_set(secrets.MQTT_USER, password = secrets.MQTT_PASSWORD)
client.connect(secrets.MQTT_SERVER)

topic = ""
payload = ""

last_topic = ""
last_payload = ""

while True:
    last_topic = topic
    last_payload = payload
    
    topic = input("\nTopic? [%s] " % last_topic).replace('\n', ' ').replace('\r', '').strip()
    payload = input("Message? [%s] " % last_payload).replace('\n', ' ').replace('\r', '').strip()

    if topic == "":
        topic = last_topic

    if payload == "":
        payload = last_payload

    client.publish(topic, payload = payload)
