from machine import ADC, Pin, reset
from utime import sleep
from sys import print_exception

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import pinmap

from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.binary_sensors.motion import MotionBinarySensor

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

motion_sensor = MotionBinarySensor(None, state)

def mqtt_send_config():
    return mqtt.publish_json(motion_sensor.config_topic(), motion_sensor.config(), retain=True)

send_failure_count = 0

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
            motion_sensor.set_attr({ "UID": HomeAssistant.UID, "IP": wifi.ip(), "MAC": wifi.mac(), "RSSI": wifi.rssi() })
            if not mqtt.publish_json(motion_sensor.state_topic(), state, reconnect=True):
                send_failure_count += 1
                print('Failed to send state (%d)' % send_failure_count)
                if send_failure_count >= 5:
                    raise Exception('Failed to send state')

        sleep(2)

except Exception as exception:
    print_exception(exception)
    for loop in range(30):
        led.value(loop % 2 == 0)
        sleep(0.5)

reset()
