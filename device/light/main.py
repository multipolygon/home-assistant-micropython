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
from lib.home_assistant.light import Light

_24hrs = 24 * 60 * 60 # seconds

## Device ##

pin = Pin(pinmap.D1, mode=Pin.OUT)

## Home Assistant ##

HomeAssistant.NAME = "Light"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

print(HomeAssistant.UID)

state = {} ## State is a 'global' object containing all sensor values

status_sensor = ConnectivityBinarySensor("Status", state)
wifi_signal_sensor = SignalStrengthSensor("WiFi", state)
light = Light(None, state)

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
        mqtt.publish_json(status_sensor.config_topic(), status_sensor.config(off_delay=_24hrs), retain=True) and
        mqtt.publish_json(status_sensor.attributes_topic(), { "ip": wifi.ip(), "mac": wifi.mac() }) and
        mqtt.publish_json(wifi_signal_sensor.config_topic(), wifi_signal_sensor.config(), retain=True) and
        mqtt.publish_json(light.config_topic(), light.config(), retain=True)
    )

def mqtt_send_state(clear_command=False):
    print("MQTT send state")
    wifi_signal_sensor.set_state(wifi.rssi())
    light.set_state(pin.value())
    print(state)
    mqtt.publish_json(status_sensor.state_topic(), state, reconnect=True)

def mqtt_receive(topic, message):
    print("MQTT receive")
    if topic == bytearray(light.command_topic()):
        status_led.on()
        if message == bytearray(light.STATE_ON):
            pin.on()
            mqtt_send_state()
        elif message == bytearray(light.STATE_OFF):
            pin.off()
            mqtt_send_state()
        status_led.off()

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
            status_led.on()
            if mqtt.connect(timeout=30):
                connection_attempts = 0
            else:
                if connection_attempts > 10:
                    raise Exception('Connection')
                connection_attempts += 1
                sleep_ms(5000)

        elif uptime() > _24hrs:
            raise Exception('Daily reset')
            
        elif not(config_sent) and wifi.rssi() > -80:
            status_led.on()
            config_sent = mqtt_send_config()
            if config_sent:
                mqtt_send_state()

        else:
            status_led.off()
            mqtt.wait_msg()

except Exception as exception:
    print_exception(exception)
    for loop in range(30):
        status_led.led.value(loop % 2 == 0)
        sleep_ms(500)

print("Reset")
reset()
