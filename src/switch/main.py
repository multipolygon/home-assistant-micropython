from machine import ADC, Pin, reset
from utime import sleep, ticks_ms, ticks_diff
from sys import print_exception

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led

from lib.home_assistant.main import HomeAssistant
# from lib.home_assistant.switch import Switch as Light
from lib.home_assistant.light import Light

## Config ##

PIR_MODE = False
RESET_INTERVAL = 24 * 60 * 60
UPDATE_INTERVAL = 10
STATE_PUBLISH_INTERVAL = 10 * 60

RELAY_PIN = pinmap.D1 ## Default: D1
BUTTON_PIN = pinmap.D3

RELAY_ON = 1
RELAY_OFF = 0
BUTTON_PRESS = 0
MOTION_DETECTED = 1

## Device ##

relay = Pin(RELAY_PIN, mode=Pin.OUT)
button = Pin(BUTTON_PIN, mode=Pin.IN)

## State ##

state = False

def on():
    global state
    state = True
    status_led.on()
    relay.value(RELAY_ON)

def off():
    global state
    state = False
    status_led.off()
    relay.value(RELAY_OFF)

def toggle():
    if relay.value() == RELAY_ON:
        off()
    else:
        on()

## Home Assistant ##

HomeAssistant.NAME = "Switch"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

print(HomeAssistant.UID)

switch = Light()

## MQTT ##

mqtt = MQTTClient(
    wifi.mac(),
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

def mqtt_publish_config():
    print("MQTT publish config")
    return mqtt.publish_json(switch.config_topic(), switch.config(), retain=True)

def mqtt_send_state():
    print("MQTT send state")
    switch.set_state(state)
    switch.set_attr({ "UID": HomeAssistant.UID, "IP": wifi.ip(), "MAC": wifi.mac(), "RSSI": wifi.rssi() })
    if not mqtt.publish_json(switch.state_topic(), switch.state(), reconnect=True):
        status_led.slow_blink()

def mqtt_send_command():
    print("MQTT send command")
    mqtt.publish(switch.command_topic(), state and switch.PAYLOAD_ON or switch.PAYLOAD_OFF, retain=True)

def mqtt_receive(topic, message):
    print("MQTT receive")
    if topic == bytearray(switch.command_topic()):
        if message == bytearray(switch.STATE_ON):
            on()
        elif message == bytearray(switch.STATE_OFF):
            off()

mqtt.set_callback(mqtt_receive)

def mqtt_connected():
    print("MQTT subscribe: " + switch.command_topic())
    mqtt.subscribe(bytearray(switch.command_topic()))

mqtt.set_connected_callback(mqtt_connected)

mqtt.connect()
mqtt.check_msg()

## Time ##

start_up_at = updated_at = state_published_at = ticks_ms()

def time_diff(time_stamp):
    return ticks_diff(ticks_ms(), time_stamp) // 1000 # seconds

def time_since_start_up():
    return time_diff(start_up_at)

def time_since_update():
    return time_diff(updated_at)

def time_since_state_published():
    return time_diff(state_published_at)

## Main Loop ##

config_sent = mqtt_publish_config()

try:
    while True:
        if time_since_start_up() > RESET_INTERVAL:
            print('Time to reset')
            reset()

        if time_since_update() > UPDATE_INTERVAL:
            print('Time to update')
            updated_at = ticks_ms()
            mqtt.check_msg()

            if time_since_state_published() > STATE_PUBLISH_INTERVAL:
                print('Time to publish state')
                state_published_at = ticks_ms()
                if not config_sent:
                    config_sent = mqtt_publish_config()
                mqtt_send_state()

        if PIR_MODE:
            if button.value() == MOTION_DETECTED and relay.value() == RELAY_OFF:
                on()
                mqtt_send_command()
                mqtt_send_state()
        else:
            if button.value() == BUTTON_PRESS:
                toggle()
                mqtt_send_command()
                mqtt_send_state()

        sleep(0.1)

except Exception as exception:
    print_exception(exception)
    status_led.fast_blink()
    sleep(10)
    status_led.off()
    reset()
