from machine import ADC, Pin, reset
from utime import sleep
from sys import print_exception

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import oled
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led

from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.binary_sensors.connectivity import ConnectivityBinarySensor
from lib.home_assistant.binary_sensors.problem import ProblemBinarySensor
from lib.home_assistant.sensors.signal_strength import SignalStrengthSensor
from lib.home_assistant.sensors.temperature import TemperatureSensor

import thermistor

HomeAssistant.NAME = "Thermometer"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

print(oled.write('POWER ON'))

adc = ADC(pinmap.A0)
probe_1 = Pin(pinmap.D5, mode=Pin.OUT)
probe_2 = Pin(pinmap.D6, mode=Pin.OUT)

state = {} ## State is a 'global' object containing all sensor values

mqtt = MQTTClient(
    wifi.mac(),
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

status_sensor = ConnectivityBinarySensor("Status", state)
fault_sensor = ProblemBinarySensor("Fault", state)
wifi_signal_sensor = SignalStrengthSensor("WiFi", state)
temperature_sensor_a = TemperatureSensor("Temp A", state)
temperature_sensor_b = TemperatureSensor("Temp B", state)

status_sensor.set_state(True)
fault_sensor.set_state(False)

def mqtt_send_config():
    print("MQTT sending config...")
    try:
        mqtt.publish_json(status_sensor.config_topic(), status_sensor.config(off_delay=3600), retain=True)
        mqtt.publish_json(status_sensor.attributes_topic(), { "ip": wifi.ip(), "mac": wifi.mac() })
        mqtt.publish_json(fault_sensor.config_topic(), fault_sensor.config(off_delay=3600), retain=True)
        mqtt.publish_json(wifi_signal_sensor.config_topic(), wifi_signal_sensor.config(), retain=True)
        mqtt.publish_json(temperature_sensor_a.config_topic(), temperature_sensor_a.config(), retain=True)
        mqtt.publish_json(temperature_sensor_b.config_topic(), temperature_sensor_b.config(), retain=True)
        print(" > sent.")
        return True
    except Exception as exception:
        print(" > Error: " + exception.__class__.__name__ + ": " + str(exception))
        return False

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

    return sum(probe_readings[id-1]) / number_of_readings

state_sent = False
config_sent = False

try:
    for loop in range(50000):
        status_led.on()
        print(loop)

        if (not(config_sent) and
            loop % 15 == 0 and ## Only try to send the config every 15 loops until success
            mqtt.is_connected() and
            wifi.rssi() > -80 and
            True):
            oled.write('', False)
            oled.write('SENDING', False)
            oled.write('CONFIG', False)
            oled.write('...')
            config_sent = mqtt_send_config()

        adc1 = read_probe(1, loop)
        adc2 = read_probe(2, loop)

        t1 = thermistor.temperature(adc1)
        t2 = thermistor.temperature(adc2)

        oled.write('%4s %s%s%s' % (wifi.is_connected() and wifi.rssi() or "--", mqtt.is_connected() and "+" or "-", config_sent and "+" or "-", state_sent and "+" or "-"), False)
        oled.write('%4d%4d' % (adc1, adc2), False)
        oled.write('%4.0f%4.0f' % (t1, t2), False)
        oled.write('%8.0d' % loop)

        if loop % number_of_readings == 0:
            print("MQTT sending state...")
            fault_sensor.set_state(False)
            temperature_sensor_a.set_state(round(t1, 2))
            temperature_sensor_b.set_state(round(t2, 2))
            wifi_signal_sensor.set_state(wifi.rssi())
            print(state)
            state_sent = mqtt.publish_json(status_sensor.state_topic(), state, reconnect=True) ## All sensors share the same state topic
            print(" > sent.")

        status_led.off()

        sleep(1)

except Exception as exception:
    try:
        oled.write('ERROR!')
        oled.write(exception.__class__.__name__)
        oled.write(str(exception))
        print_exception(exception)
        fault_sensor.set_state(True)
        mqtt.publish_json(fault_sensor.state_topic(), state)
        mqtt.publish_json(fault_sensor.attributes_topic(), { "reason": exception.__class__.__name__ + ": " + str(exception) })
    except:
        pass

try:
    status_led.off() 
    print(oled.write('RESET...'))
except:
    pass

sleep(10)

reset()
