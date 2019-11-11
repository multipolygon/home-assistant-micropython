from machine import ADC, Pin, reset
from utime import sleep

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led

from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.binary_sensors.power import PowerBinarySensor

HomeAssistant.NAME = "Power Detector"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

status_led.on()

mqtt = MQTTClient(
    wifi.mac(),    
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

sensor = PowerBinarySensor()
sensor.set_state(True)

def mqtt_connected_callback():
    print('MQTT config...')
    mqtt.publish_json(sensor.config_topic(), sensor.config(off_delay=140), retain=True)

mqtt.set_connected_callback(mqtt_connected_callback)

for loop in range(24 * 60):
    print(loop)
    if not mqtt.publish_json(sensor.state_topic(), sensor.state(), reconnect=True):
        for blink in range(10):
            status_led.led.value(blink % 2 == 0)
            sleep(0.5)
    sleep(60)

print("Daily reset...")
reset()
