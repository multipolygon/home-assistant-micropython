import secrets
import wifi
from umqtt_robust import MQTTClient
import homeassistant

import oled

oled.write('POWER ON')
oled.write(homeassistant.UID)

ha_status = homeassistant.StatusSensor()
ha_wifi_signal_strength = homeassistant.WiFiSignalStrengthSensor()
ha_temperature_1 = homeassistant.TemperatureSensor() 
ha_temperature_2 = homeassistant.TemperatureSensor('temperature2')

mqtt = MQTTClient(homeassistant.IDENT, secrets.MQTT_SERVER, user=secrets.MQTT_USER, password=secrets.MQTT_PASSWORD)

def mqtt_connected_callback():
    print('MQTT sending config...')
    mqtt.publish_json(ha_status.config_topic(), ha_status.config(off_delay=60), retain=True)
    mqtt.publish_json(ha_status.attributes_topic(), { "ip_address": wifi.ip() })
    mqtt.publish_json(ha_wifi_signal_strength.config_topic(), ha_wifi_signal_strength.config(expire_after=60), retain=True)
    mqtt.publish_json(ha_temperature_1.config_topic(), ha_temperature_1.config(expire_after=60), retain=True)
    mqtt.publish_json(ha_temperature_2.config_topic(), ha_temperature_2.config(expire_after=60), retain=True)
    print('MQTT config sent.')

mqtt.set_connected_callback(mqtt_connected_callback)
mqtt.set_last_will(ha_status.state_topic(), ha_status.payload_off())
mqtt.connect()

if wifi.isconnected():
    oled.write('%8s' % wifi.sigbars())
    ip = wifi.ip()
    oled.write(ip[0:8])
    oled.write(ip[8:])
else:
    oled.write('No WiFi!')

#################################################################################

from machine import ADC, Pin
from utime import sleep
import esp

import oled
import pinmap
import status_led

adc = ADC(pinmap.A0)
probe_1 = Pin(pinmap.D5, mode=Pin.OUT)
probe_2 = Pin(pinmap.D6, mode=Pin.OUT)
button = Pin(pinmap.D3, mode=Pin.IN)
relay = Pin(pinmap.D8, mode=Pin.OUT)

probe_1.on()
probe_2.off()
relay.off()

number_of_readings = 10
probe_readings = { 0: ([adc.read()] * number_of_readings), 1: ([adc.read()] * number_of_readings) }
cycle = -1

def read_probe(id):
    if id == 1:
        probe_1.on()
        probe_2.off()
    else:
        probe_1.off()
        probe_2.on()
    
    sleep(1) # Delay may help give pin time to stabilise?

    probe_readings[id-1][cycle] = adc.read()
        
    return sum(probe_readings[id-1]) / number_of_readings

def temperature(val):
    # https://www.wolframalpha.com/input/?i=linear+fit+%7B0%2C62%7D%2C%7B17.6%2C135%7D%2C%7B42.3%2C270%7D%2C%7B63%2C434%7D%2C%7B94.5%2C643%7D
    return (val - 36.1997) / 6.26956

sleep(2)

while True:
    status_led.on()
    
    print('')

    cycle = (cycle + 1) % number_of_readings
    print(cycle)

    r1 = read_probe(1)
    r2 = read_probe(2)

    print(probe_readings)

    t1 = temperature(r1)
    t2 = temperature(r2)

    solar_collector = t1
    storage_tank = t2

    if solar_collector > 98:
        ## too hot, don't want water to vaporise
        relay.off()
    elif storage_tank > 60:
        ## water is hot enough
        relay.off()
    elif solar_collector - storage_tank > 12:
        ## water pump on
        relay.on()
    else:
        relay.off()

    oled.write('%8s' % wifi.sigbars(), False)
    oled.write('%4d%4d' % (r1, r2), False)
    oled.write('%4.0f%4.0f' % (t1, t2), False)
    oled.write('%8s' % (relay.value() and 'ON' or 'OFF'), True)

    status_led.off()

    if cycle == 0:
        mqtt.publish(ha_status.state_topic(), ha_status.payload_on(), reconnect=True)
        mqtt.publish(ha_wifi_signal_strength.state_topic(), str(wifi.rssi()))
        mqtt.publish(ha_temperature_1.state_topic(), "%.2f" % t1)
        mqtt.publish(ha_temperature_2.state_topic(), "%.2f" % t2)

    sleep(relay.value() and 1 or 10)
