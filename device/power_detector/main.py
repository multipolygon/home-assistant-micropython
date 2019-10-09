from machine import ADC, Pin
from utime import sleep

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led

from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.binary_sensors.connectivity import ConnectivityBinarySensor
from lib.home_assistant.binary_sensors.power import PowerBinarySensor
from lib.home_assistant.sensors.signal_strength import SignalStrengthSensor

HomeAssistant.NAME = "Power Detector"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

status_led.on()

mqtt = MQTTClient(
    wifi.mac(),    
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

state = {}
status_sensor = ConnectivityBinarySensor("Status", state)
status_sensor.set_state(False)
power_sensor = PowerBinarySensor(None, state)
power_sensor.set_state(False)
mqtt.set_last_will_json(status_sensor.state_topic(), state)
status_sensor.set_state(True)
power_sensor.set_state(True)

wifi_signal_sensor = SignalStrengthSensor("WiFi", state)

def mqtt_connected_callback():
    # print('MQTT sending config...')
    mqtt.publish_json(status_sensor.config_topic(), status_sensor.config(off_delay=120), retain=True)
    mqtt.publish_json(status_sensor.attributes_topic(), { "ip": wifi.ip(), "mac": wifi.mac() })
    mqtt.publish_json(wifi_signal_sensor.config_topic(), wifi_signal_sensor.config(), retain=True)
    mqtt.publish_json(power_sensor.config_topic(), power_sensor.config(off_delay=120), retain=True)
    # print('MQTT config sent.')

mqtt.set_connected_callback(mqtt_connected_callback)

while True:
    mqtt.connect()

    for loop in range(2000):
        # print('')
        # print(loop)
        wifi_signal_sensor.set_state(wifi.rssi())
        mqtt.publish_json(power_sensor.state_topic(), state, reconnect=True)
        sleep(60)
