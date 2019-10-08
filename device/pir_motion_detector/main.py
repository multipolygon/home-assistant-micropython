from machine import ADC, Pin
from utime import sleep

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import pinmap

from lib.home_assistant.binary_sensors.connectivity import ConnectivityBinarySensor
from lib.home_assistant.binary_sensors.motion import MotionBinarySensor
from lib.home_assistant.sensors.signal_strength import SignalStrengthSensor

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

status_sensor = ConnectivityBinarySensor("Status", state, secrets.MQTT_USER)
status_sensor.set_state(False)
motion_sensor = MotionBinarySensor(None, state, secrets.MQTT_USER)
motion_sensor.set_state(False)
mqtt.set_last_will_json(status_sensor.state_topic(), state)
status_sensor.set_state(True)

wifi_signal_sensor = SignalStrengthSensor("WiFi Signal Strength", state, secrets.MQTT_USER)

def mqtt_connected_callback():
    print('MQTT sending config...')
    mqtt.publish_json(status_sensor.config_topic(), status_sensor.config(off_delay=60), retain=True)
    status_sensor.set_attributes({ "ip": wifi.ip(), "mac": wifi.mac() })
    mqtt.publish_json(wifi_signal_sensor.config_topic(), wifi_signal_sensor.config(), retain=True)
    mqtt.publish_json(motion_sensor.config_topic(), motion_sensor.config(off_delay=60), retain=True)
    status_sensor.set_attributes(None)
    print('MQTT config sent.')

mqtt.set_connected_callback(mqtt_connected_callback)

while True:
    mqtt.connect()

    for loop in range(50000):
        print('')
        print(loop)

        led.value(not sensor.value())

        if sensor.value() != detected or loop % 30 == 0:
            detected = sensor.value()
            motion_sensor.set_state(detected)
            mqtt.publish_json(motion_sensor.state_topic(), state, reconnect=True)

        sleep(2)
