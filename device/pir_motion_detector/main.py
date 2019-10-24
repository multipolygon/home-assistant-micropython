from machine import ADC, Pin, reset
from utime import sleep
from sys import print_exception

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import pinmap

from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.binary_sensors.connectivity import ConnectivityBinarySensor
from lib.home_assistant.binary_sensors.motion import MotionBinarySensor
from lib.home_assistant.sensors.signal_strength import SignalStrengthSensor

HomeAssistant.NAME = "PIR Motion Sensor"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

led = Pin(pinmap.LED, Pin.OUT)
sensor = Pin(pinmap.D3, mode=Pin.IN)
detected = sensor.value()
state = {}

mqtt = MQTTClient(
    wifi.mac(),    
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

status_sensor = ConnectivityBinarySensor("Status", state)
motion_sensor = MotionBinarySensor(None, state)
wifi_signal_sensor = SignalStrengthSensor("WiFi", state)

def mqtt_send_config():
    return (
        mqtt.publish_json(status_sensor.config_topic(), status_sensor.config(off_delay=900), retain=True) and
        mqtt.publish_json(status_sensor.attributes_topic(), { "ip": wifi.ip(), "mac": wifi.mac() }) and 
        mqtt.publish_json(wifi_signal_sensor.config_topic(), wifi_signal_sensor.config(), retain=True) and
        mqtt.publish_json(motion_sensor.config_topic(), motion_sensor.config(off_delay=900), retain=True)
    )

status_sensor.set_state(True)
motion_sensor.set_state(detected)

try:
    led.value(False)
    
    if not mqtt.connect():
        raise Exception('Failed to connect')

    if not mqtt_send_config():
        raise Exception('Failed to send config')

    for loop in range(50000):
        print(loop)

        led.value(not sensor.value())

        if sensor.value() != detected or loop % 30 == 0:
            detected = sensor.value()
            motion_sensor.set_state(detected)
            wifi_signal_sensor.set_state(wifi.rssi())
            if not mqtt.publish_json(motion_sensor.state_topic(), state, reconnect=True):
                raise Exception('Failed to publish state')

        sleep(2)

except Exception as exception:
    print_exception(exception)
    for loop in range(30):
        led.value(loop % 2 == 0)
        sleep(0.5)

reset()
