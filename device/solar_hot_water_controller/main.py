from machine import ADC, Pin
from utime import sleep

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import oled
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led

from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.binary_sensors.connectivity import ConnectivityBinarySensor
from lib.home_assistant.sensors.signal_strength import SignalStrengthSensor
from lib.home_assistant.sensors.temperature import TemperatureSensor
from lib.home_assistant.switch import Switch

import controller
import thermistor

HomeAssistant.NAME = "Solar HWS"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

oled.write('POWER ON')

adc = ADC(pinmap.A0)
button = Pin(pinmap.D3, mode=Pin.IN)
probe_1 = Pin(pinmap.D5, mode=Pin.OUT)
probe_2 = Pin(pinmap.D6, mode=Pin.OUT)
relay = Pin(pinmap.D8, mode=Pin.OUT)
state = {} ## State is a 'global' object containing all sensor data

mqtt = MQTTClient(
    wifi.mac(),
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

status_sensor = ConnectivityBinarySensor("Status", state)
status_sensor.set_state(False)
mqtt.set_last_will_json(status_sensor.state_topic(), state)
status_sensor.set_state(True)

wifi_signal_sensor = SignalStrengthSensor("WiFi", state)
temperature_sensor_a = TemperatureSensor('Temp A', state)
temperature_sensor_b = TemperatureSensor('Temp B', state)
relay_switch = Switch('Relay', state)

def mqtt_connected_callback():
    # print('MQTT sending config...')
    mqtt.publish_json(status_sensor.config_topic(), status_sensor.config(), retain=True)
    mqtt.publish_json(status_sensor.attributes_topic(), { "ip": wifi.ip(), "mac": wifi.mac() })
    mqtt.publish_json(wifi_signal_sensor.config_topic(), wifi_signal_sensor.config(), retain=True)
    mqtt.publish_json(temperature_sensor_a.config_topic(), temperature_sensor_a.config(), retain=True)
    mqtt.publish_json(temperature_sensor_b.config_topic(), temperature_sensor_b.config(), retain=True)
    mqtt.publish_json(relay_switch.config_topic(), relay_switch.config(), retain=True)
    # print('MQTT config sent.')

mqtt.set_connected_callback(mqtt_connected_callback)

number_of_readings = 10
probe_readings = {}

def read_probe(id, loop):
    if id == 1:
        probe_1.on()
        probe_2.off()
    else:
        probe_1.off()
        probe_2.on()
    
    sleep(1) # Delay may allow to stabilise?

    try:
        n = loop % number_of_readings
        probe_readings[id-1][n] = adc.read()
    except KeyError:
        probe_readings[id-1] = [adc.read()] * number_of_readings

    # print(probe_readings[id-1])
        
    return sum(probe_readings[id-1]) / number_of_readings

while True:
    status_led.on()
    oled.write('MQTT...')
    mqtt.connect()
    if wifi.is_connected():
        oled.write('WiFi%4d' % wifi.rssi())
        ip = wifi.ip()
        oled.write(ip[0:8])
        oled.write(ip[8:])
        if mqtt.is_connected():
            oled.write(wifi.uid())
        else:
            oled.write('MQTT Err')
    else:
        oled.write('No WiFi!')
    status_led.off()
    sleep(3)

    for loop in range(1000):
        # print('')
        # print(loop)
        status_led.on()

        adc1 = read_probe(1, loop)
        adc2 = read_probe(2, loop)

        t1 = thermistor.temperature(adc1)
        t2 = thermistor.temperature(adc2)

        relay_was = relay.value()
        controller.logic(t1, t2, relay)

        oled.write('%4s%4s' % (wifi.is_connected() and wifi.rssi() or 'Err', mqtt.is_connected() and 'OK' or 'Err'), False)
        oled.write('%4d%4d' % (adc1, adc2), False)
        oled.write('%4.0f%4.0f' % (t1, t2), False)
        oled.write('%8s' % (relay.value() and 'ON' or 'OFF'), True)

        if relay_was != relay.value() or loop % (relay.value() and 10 or 100) == 0:
            temperature_sensor_a.set_state(round(t1, 2))
            temperature_sensor_b.set_state(round(t2, 2))
            relay_switch.set_state(relay.value())
            wifi_signal_sensor.set_state(wifi.rssi())
            mqtt.publish_json(status_sensor.state_topic(), state, reconnect=True) ## Note, all sensors share the same state topic.
            
        status_led.off()

        sleep(1)
