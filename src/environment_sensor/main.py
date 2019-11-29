from machine import ADC, Pin, I2C, reset_cause, DEEPSLEEP_RESET
from utime import time, sleep
from esp import deepsleep
import gc

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import oled
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led

from lib.esp8266.bh1750.bh1750 import BH1750
from lib.esp8266.sht30.sht30 import SHT30

from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.sensor import Sensor
from lib.home_assistant.sensors.humidity import HumiditySensor
from lib.home_assistant.sensors.illuminance import IlluminanceSensor
from lib.home_assistant.sensors.temperature import TemperatureSensor
from lib.home_assistant.sensors.battery import BatterySensor

## Config

ADC_BATTERY_VOLTAGE = False
SLEEP_FOR = 30 # minutes
HomeAssistant.NAME = "Env Sensor"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

## Boot

print(HomeAssistant.UID)

status_led.off()
oled.write('POWER ON')
oled.write('')
oled.write('')
oled.write('')
sleep(1)

## Device Sensors

def read_temperature_humidity_sensor():
    sht30 = SHT30(scl_pin = pinmap.SCL, sda_pin = pinmap.SDA)
    if sht30.is_present():
        return sht30.measure()
    else:
        return (None, None)

def read_light_sensor():
    i2c = I2C(scl=Pin(pinmap.SCL), sda=Pin(pinmap.SDA))
    bh1750 = BH1750(i2c)
    if bh1750.is_present():
        lux = bh1750.luminance(BH1750.ONCE_HIRES_1)
        bh1750.off()
        return lux
    else:
        return None

def read_adc():
    return ADC(pinmap.A0).read() / 1024 * 100
    
print('DHT sensor...')
temperature, humidity = read_temperature_humidity_sensor()
if temperature != None:
    print(oled.write('%7.1fC' % temperature))
if humidity != None:
    print(oled.write('%6.1f%%RH' % humidity))

print('Light sensor...')
light_level = read_light_sensor()
if light_level != None:
    print(oled.write('%6.1flx' % light_level))

print('ADC...')
adc_reading = read_adc()
print(oled.write('%6.1f%%V' % adc_reading))

gc.collect()
sleep(5)

## Home Assistant

print('HA sensors...')
state = {} ## State is a 'global' object containing all sensor data
analog_sensor = BatterySensor(None, state) if ADC_BATTERY_VOLTAGE else Sensor('Analog', state)
if temperature:
    temperature_sensor = TemperatureSensor("Temp", state)
if humidity:
    humidity_sensor = HumiditySensor("Humid", state)
if light_level:
    illuminance_sensor = IlluminanceSensor("Lux", state)

## MQTT

mqtt = MQTTClient(
    wifi.mac(),
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

def publish_config():
    print('MQTT config...')
    EXPIRE_AFTER = SLEEP_FOR * 60 * 2.5
    mqtt.publish_json(analog_sensor.config_topic(), analog_sensor.config(expire_after=EXPIRE_AFTER), retain=True)
    gc.collect()
    if temperature != None:
        mqtt.publish_json(temperature_sensor.config_topic(), temperature_sensor.config(expire_after=EXPIRE_AFTER), retain=True)
        gc.collect()
    if humidity != None:
        mqtt.publish_json(humidity_sensor.config_topic(), humidity_sensor.config(expire_after=EXPIRE_AFTER), retain=True)
        gc.collect()
    if light_level != None:
        mqtt.publish_json(illuminance_sensor.config_topic(), illuminance_sensor.config(expire_after=EXPIRE_AFTER), retain=True)
        gc.collect()

## Publish-Retry Loop

for loop in range(3):
    print("Loop: %d" % loop)

    print('MQTT connecting...')
    mqtt.connect()
    oled.write('WiFi%4s' % wifi.rssi() if wifi.is_connected() else 'ERR')
    oled.write('MQTT%4s' % 'OK' if mqtt.is_connected() else 'ERR')
    
    if mqtt.is_connected():
        if reset_cause() != DEEPSLEEP_RESET:
            publish_config()

        print('Set state...')
        analog_sensor.set_state(round(adc_reading, 2))
        if temperature != None:
            temperature_sensor.set_state(round(temperature, 2))
        if humidity != None:
            humidity_sensor.set_state(round(humidity, 2))
        if light_level != None:
            illuminance_sensor.set_state(round(light_level, 2))

        print('Set attr...')
        analog_sensor.set_attr({
            "UID": HomeAssistant.UID,
            "IP": wifi.ip(),
            "MAC": wifi.mac(),
            "RSSI": wifi.rssi(),
            "Interval": SLEEP_FOR,
        })

        print('MQTT state...')
        ## Note, all sensors share the same state and attr topic:
        mqtt.publish_json(analog_sensor.state_topic(), state)

        print('Done.')
        break

    else:
        print('Not connected!')
        status_led.on()
        sleep(5)

## Deep Sleep

sleep(10)

mqtt.disconnect()
wifi.disconnect()

status_led.off()
oled.power_off()

print('Sleep for %d min...' % SLEEP_FOR)
## https://docs.micropython.org/en/latest/library/esp.html#esp.deepsleep
## Note, GPIO pin 16 (or D0 on the Wemos D1 Mini) must be wired to the Reset pin. See README
## Note: ESP8266 only - use machine.deepsleep() on ESP32
## https://docs.micropython.org/en/latest/esp8266/tutorial/powerctrl.html#deep-sleep-mode

deepsleep(SLEEP_FOR * 60 * 1000000) 
