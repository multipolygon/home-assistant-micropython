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

_24hrs = 24 * 60 * 60 # seconds

## Device ##

pin = Pin(pinmap.D1, mode=Pin.OUT) ## Relay default is D1

## Home Assistant ##

HomeAssistant.NAME = "Light"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

print(HomeAssistant.UID)

light = Light()

## MQTT ##

mqtt = MQTTClient(
    wifi.mac(),
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

def mqtt_send_config():
    print("MQTT send config")
    return mqtt.publish_json(light.config_topic(), light.config(), retain=True)

def mqtt_send_state(clear_command=False):
    print("MQTT send state")
    status_led.led.value(not pin.value()) ## LED is inverted
    light.set_state(pin.value())
    light.set_attr({ "UID": HomeAssistant.UID, "IP": wifi.ip(), "MAC": wifi.mac(), "RSSI": wifi.rssi() })
    mqtt.publish_json(light.state_topic(), light.state(), reconnect=True)

def mqtt_receive(topic, message):
    print("MQTT receive")
    if topic == bytearray(light.command_topic()):
        if message == bytearray(light.STATE_ON):
            pin.on()
            mqtt_send_state()
        elif message == bytearray(light.STATE_OFF):
            pin.off()
            mqtt_send_state()

mqtt.set_callback(mqtt_receive)

def mqtt_connected():
    print("MQTT subscribe: " + light.command_topic())
    mqtt.subscribe(bytearray(light.command_topic()))

mqtt.set_connected_callback(mqtt_connected)

## Time ##

startup = ticks_ms()

def uptime():
    return ticks_diff(ticks_ms(), startup) // 1000 # seconds

## Main Loop ##

connection_attempts = 0
config_sent = False

try:
    while True:
        if not mqtt.is_connected():
            if mqtt.connect(timeout=30):
                connection_attempts = 0
            else:
                if connection_attempts > 10:
                    raise Exception('Connection')
                connection_attempts += 1
                sleep(5)

        elif uptime() > _24hrs:
            raise Exception('Daily reset')
            
        elif not(config_sent) and wifi.rssi() > -80:
            config_sent = mqtt_send_config()
            if config_sent:
                mqtt_send_state()

        else:
            mqtt.wait_msg()

except Exception as exception:
    print_exception(exception)
    for loop in range(30):
        status_led.led.value(loop % 2 == 0)
        sleep(0.5)

print("Reset")
reset()
