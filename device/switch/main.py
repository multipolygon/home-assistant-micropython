from machine import ADC, Pin, reset
from utime import sleep_ms, ticks_ms, ticks_diff
from sys import print_exception

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led

from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.binary_sensors.connectivity import ConnectivityBinarySensor
from lib.home_assistant.sensors.signal_strength import SignalStrengthSensor
from lib.home_assistant.switch import Switch

## Device ##

relay = Pin(pinmap.D1, mode=Pin.OUT)
button = Pin(pinmap.D3, mode=Pin.IN)

PIR_MODE = True

RELAY_OFF = 0
BUTTON_PRESS = 0
MOTION_DETECTED = 1

## Home Assistant ##

HomeAssistant.NAME = "Switch"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

print(HomeAssistant.UID)

state = {} ## State is a 'global' object containing all sensor values

status_sensor = ConnectivityBinarySensor("Status", state)
wifi_signal_sensor = SignalStrengthSensor("WiFi", state)
relay_switch = Switch("Relay", state)

status_sensor.set_state(True)

## MQTT ##

mqtt = MQTTClient(
    wifi.mac(),
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

def mqtt_send_config():
    print("MQTT send config")
    return (
        mqtt.publish_json(status_sensor.config_topic(), status_sensor.config(off_delay=3600), retain=True) and
        mqtt.publish_json(status_sensor.attributes_topic(), { "ip": wifi.ip(), "mac": wifi.mac() }) and
        mqtt.publish_json(wifi_signal_sensor.config_topic(), wifi_signal_sensor.config(), retain=True) and
        mqtt.publish_json(relay_switch.config_topic(), relay_switch.config(), retain=True)
    )

def mqtt_send_state(clear_command=False):
    print("MQTT send state")
    wifi_signal_sensor.set_state(wifi.rssi())
    relay_switch.set_state(relay.value())
    print(state)
    mqtt.publish_json(status_sensor.state_topic(), state, reconnect=True)
    if clear_command:
        print("MQTT clear command")
        mqtt.publish(relay_switch.command_topic(), "OVERRIDE", retain=True)

def mqtt_receive(topic, message):
    print("MQTT receive")
    if topic == bytearray(relay_switch.command_topic()):
        status_led.on()
        if message == bytearray(relay_switch.STATE_ON):
            relay.on()
            mqtt_send_state()
        elif message == bytearray(relay_switch.STATE_OFF):
            relay.off()
            mqtt_send_state()
        status_led.off()

mqtt.set_callback(mqtt_receive)

def mqtt_connected():
    print("MQTT subscribe: " + relay_switch.command_topic())
    mqtt.subscribe(bytearray(relay_switch.command_topic()))

mqtt.set_connected_callback(mqtt_connected)

## Time ##

startup = ticks_ms()
_24hrs = 24 * 60 * 60 # seconds

def uptime():
    return ticks_diff(ticks_ms(), startup) // 1000 # seconds

## Main Loop ##

config_sent = False

try:
    while True:
        for loop in range(10):
            t = uptime()

            if t > _24hrs:
                raise Exception('Daily reset')

            if mqtt.is_connected():
                if loop == 0:
                    mqtt.check_msg()

                if not(config_sent) and t % 10 == 0 and wifi.rssi() > -80:
                    status_led.on()
                    config_sent = mqtt_send_config()
                    status_led.off()

                if t % 60 == 0:
                    mqtt_send_state()

            elif t % 10 == 0:
                print("MQTT connect")
                status_led.on()
                mqtt.connect()
                status_led.off()

            if not(PIR_MODE) and button.value() == BUTTON_PRESS:
                status_led.on()
                relay.value(not(relay.value()))
                mqtt_send_state(True)
                sleep_ms(1000)
                status_led.off()
            elif PIR_MODE and relay.value() == RELAY_OFF and button.value() == MOTION_DETECTED:
                status_led.on()
                relay.on()
                mqtt_send_state(True)
                sleep_ms(1000)
                status_led.off()
            else:
                sleep_ms(50)

except Exception as exception:
    print_exception(exception)
    for loop in range(20):
        status_led.led.value(loop % 2 == 0)
        sleep_ms(500)

print("Reset")
reset()
