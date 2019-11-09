from machine import ADC, Pin, reset
from utime import sleep, ticks_ms, ticks_diff
from sys import print_exception

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led

from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.light import Light
# from lib.home_assistant.switch import Switch

## Device ##

relay = Pin(pinmap.D1, mode=Pin.OUT) ## Default: D1
button = Pin(pinmap.D3, mode=Pin.IN)

PIR_MODE = True

RELAY_ON = 1
RELAY_OFF = 0
BUTTON_PRESS = 0
MOTION_DETECTED = 1

## Home Assistant ##

HomeAssistant.NAME = "Switch"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

print(HomeAssistant.UID)

switch = Switch() ## or Light()

## MQTT ##

mqtt = MQTTClient(
    wifi.mac(),
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

def mqtt_send_config():
    print("MQTT send config")
    return mqtt.publish_json(switch.config_topic(), switch.config(), retain=True)

def mqtt_send_state(clear_command=False):
    print("MQTT send state")
    status_led.led.value(relay.value() != RELAY_ON) ## LED is inverted
    switch.set_state(relay.value() == RELAY_ON)
    switch.set_attr({ "UID": HomeAssistant.UID, "IP": wifi.ip(), "MAC": wifi.mac(), "RSSI": wifi.rssi() })
    mqtt.publish_json(switch.state_topic(), switch.state(), reconnect=True)
    if clear_command:
        print("MQTT clear command")
        mqtt.publish(switch.command_topic(), "OVERRIDE", retain=True)

def mqtt_receive(topic, message):
    print("MQTT receive")
    if topic == bytearray(switch.command_topic()):
        if message == bytearray(switch.STATE_ON):
            relay.on()
            mqtt_send_state()
        elif message == bytearray(switch.STATE_OFF):
            relay.off()
            mqtt_send_state()

mqtt.set_callback(mqtt_receive)

def mqtt_connected():
    print("MQTT subscribe: " + switch.command_topic())
    mqtt.subscribe(bytearray(switch.command_topic()))

mqtt.set_connected_callback(mqtt_connected)

## Time ##

startup = ticks_ms()

def uptime():
    return ticks_diff(ticks_ms(), startup) // 1000 # seconds

## Main Loop ##

config_sent = False

try:
    while True:
        t = uptime() ## seconds

        if t > 24 * 60 * 60:
            raise Exception('Daily reset')

        if mqtt.is_connected():
            print('MQTT Check msg')
            mqtt.check_msg()

            if not(config_sent) and wifi.rssi() > -80:
                config_sent = mqtt_send_config()

            if t % 600 == 0:
                mqtt_send_state()

        elif t % 10 == 0:
            print("MQTT connect")
            mqtt.connect()

        for loop in range(100):
            if PIR_MODE and relay.value() == RELAY_OFF and button.value() == MOTION_DETECTED:
                relay.on()
                mqtt_send_state(True)
                sleep(1)
            elif not(PIR_MODE) and button.value() == BUTTON_PRESS:
                relay.value(not(relay.value()))
                mqtt_send_state(True)
                sleep(1)
            else:
                sleep(0.1)

except Exception as exception:
    print_exception(exception)
    for loop in range(20):
        status_led.led.value(loop % 2 == 0)
        sleep_ms(500)

print("Reset")
reset()
