import os
import datetime
import re
import paho.mqtt.client as mqtt
import json
from argparse import ArgumentParser
from time import sleep
from tabulate import tabulate

def args():
    p = ArgumentParser()
    p.add_argument("--secrets", '-s', action="store", type=str, help='Transfer specified file as secrets.json')
    p.add_argument("--all", action="store_true", help="Clear all.")
    return p.parse_args()

args = args()

headers=["X", "Manuf", "Model", "UID", "Version", "Topic"]
messages = []

def on_message(client, userdata, message):
    if message.retain:
        config = json.loads(message.payload)
        dev = config["dev"] if "dev" in config else { "name": "-", "mdl": "-", "mf": "-", "sw": "-" }
        messages.append([
            "-",
            dev["mf"],
            dev["mdl"],
            dev["ids"],
            dev["sw"],
            message.topic.replace(base_topic, ''),
        ])

with open(args.secrets) as f:
    secrets = json.loads(f.read())

client = mqtt.Client()
client.username_pw_set(secrets['MQTT_USER'], password = secrets['MQTT_PASSWORD'])

client.on_message = on_message

client.connect(secrets['MQTT_SERVER'])

print('SERVER: %s' % secrets['MQTT_SERVER'])
print('USER: %s' % secrets['MQTT_USER'])

base_topic = ((secrets["MQTT_PREFIX"] + "/") if secrets["MQTT_PREFIX"] else "") + "homeassistant"
print('base_topic', base_topic)

client.subscribe(base_topic + "/#")

print('Running...')

client.loop_start()

sleep(3)

client.loop_stop(force=False)

sort_key = 1

def _sort_messages():
    global messages
    messages = sorted(messages, key = lambda x: x[0] + x[sort_key])

_sort_messages()

def sort():
    global sort_key
    print(tabulate(enumerate(headers)))
    sort_key = int(input("? ").strip())
        
def _row():
    return input("Row? ").strip()

def _col(c):
    return headers.index(c)

def _delete(r):
    # print(tabulate([r], headers=headers))
    t = base_topic + r[_col("Topic")]
    print(t)
    p = client.publish(t, payload=None, retain=True)
    p.wait_for_publish()
    print('Done:', p.rc)
    r[0] = "X"

def delete():
    n = _row()
    if n:
        _delete(messages[int(n)])

def delete_device():
    n = _row()
    if n:
        d = messages[int(n)][_col("Device")]
        print("Device:", d)
        for r in messages:
            if r[_col("Device")] == d:
                _delete(r)
        
commands = {
    'd': 'Delete',
    'dd': 'Delete device',
    's': 'Sort',
}

def help():
    print(tabulate(commands.items()))

functions = {
    'help': help,
    'h': help,
    'd': delete,
    'dd': delete_device,
    's': sort,
}

while True:
    _sort_messages()
    print(tabulate(messages, headers=headers, showindex=True))
    cmd = input("Command? ").strip()
    if cmd in functions:
        if cmd in commands:
            print(commands[cmd])
        functions[cmd]()
