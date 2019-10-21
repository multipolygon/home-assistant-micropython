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
from lib.home_assistant.switch import Switch

import controller
import thermistor

HomeAssistant.NAME = "Solar HWS"
HomeAssistant.UID = "Solar HWS"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

print(oled.write('POWER ON'))

adc = ADC(pinmap.A0)
button = Pin(pinmap.D3, mode=Pin.IN)
probe_1 = Pin(pinmap.D5, mode=Pin.OUT)
probe_2 = Pin(pinmap.D6, mode=Pin.OUT)
relay = Pin(pinmap.D8, mode=Pin.OUT)
relay.value(0) # off

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
relay_switch = Switch("Relay", state)

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
        mqtt.publish_json(relay_switch.config_topic(), relay_switch.config(), retain=True)
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
            not(relay.value()) and ## There may be too much interference from pump if relay is on
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

        t1 = thermistor.solar_collector(adc1)
        t2 = thermistor.storage_tank(adc2)

        relay_was = relay.value()
        relay.value(controller.logic(t1, t2, relay.value() == 1))

        oled.write('%4s %s%s%s' % (wifi.is_connected() and wifi.rssi() or "--", mqtt.is_connected() and "+" or "-", config_sent and "+" or "-", state_sent and "+" or "-"), False)
        oled.write('%4d%4d' % (adc1, adc2), False)
        oled.write('%4.0f%4.0f' % (t1, t2), False)
        oled.write('%4.0f%4s' % (controller.timer(), controller.operating_mode and (relay.value() and 'ON' or 'OFF') or 'ERR'))

        if relay_was != relay.value() or loop % (relay.value() and 10 or 100) == 0:
            print("MQTT sending state...")
            fault_sensor.set_state(controller.operating_mode == controller.FAULT)
            temperature_sensor_a.set_state(round(t1, 2))
            temperature_sensor_b.set_state(round(t2, 2))
            relay_switch.set_state(relay.value())
            wifi_signal_sensor.set_state(wifi.rssi())
            print(state)
            state_sent = mqtt.publish_json(status_sensor.state_topic(), state, reconnect=True) ## All sensors share the same state topic
            if controller.operating_mode == controller.FAULT:
                mqtt.publish_json(fault_sensor.attributes_topic(), { "reason": controller.fault_reason })
                
            print(" > sent.")

        status_led.off()

        sleep(1)

except Exception as exception:
    try:
        relay.off()
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
    relay.off()
    status_led.on() 
    print(oled.write('RESET...'))
except:
    pass

sleep(10)

reset()
