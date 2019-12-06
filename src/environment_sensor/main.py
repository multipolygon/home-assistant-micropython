from esp import deepsleep
from lib import secrets
from lib.esp8266.bh1750.bh1750 import BH1750
from lib.esp8266.sht30.sht30 import SHT30
from lib.esp8266.wemos.d1mini import oled
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.sensor import Sensor
from lib.home_assistant.sensors.battery import BatterySensor
from lib.home_assistant.sensors.humidity import HumiditySensor
from lib.home_assistant.sensors.illuminance import IlluminanceSensor
from lib.home_assistant.sensors.temperature import TemperatureSensor
from lib.home_assistant_mqtt import HomeAssistantMQTT
from lib.mqtt import MQTTClient
from lib.wifi import WiFi
from machine import ADC, Pin, I2C, reset_cause, DEEPSLEEP_RESET
from utime import time, sleep
import config
import gc

print(HomeAssistant.UID)

HomeAssistant.NAME = config.NAME
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

status_led.off()
oled.write('POWER ON')
oled.write('')
oled.write('')
oled.write('')
sleep(1)

## Device Sensors ##

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

## Home Assistant ##

print('HA sensors...')

ha = HomeAssistantMQTT(WiFi, MQTTClient, secrets)

ha.set_attribute("Interval", config.SLEEP_FOR)

opt = { 'expire_after': config.SLEEP_FOR * 60 * 2.5 }

if config.ADC_BATTERY_VOLTAGE:
    analog_sensor = ha.register('Battery', BatterySensor, opt)
else:
    analog_sensor = ha.register('Analog', Sensor, opt)
    
temperature_sensor = ha.register('Temp', TemperatureSensor, opt)
humidity_sensor = ha.register('Humid', HumiditySensor, opt)
illuminance_sensor = ha.register('Lux', IlluminanceSensor, opt)

print('Set state...')

analog_sensor.set_state(round(adc_reading, 2))

if temperature != None:
    temperature_sensor.set_state(round(temperature, 2))
    
if humidity != None:
    humidity_sensor.set_state(round(humidity, 2))
    
if light_level != None:
    illuminance_sensor.set_state(round(light_level, 2))

gc.collect()

## Publish-Retry Loop ##

ha.send_config_on_connect = reset_cause() != DEEPSLEEP_RESET

for loop in range(3):
    print("Loop: %d" % loop)

    print('MQTT connecting...')
    ha.connect()
    
    print(oled.write('WiFi%4s' % ha.wifi.rssi() if ha.wifi.is_connected() else 'ERR'))
    print(oled.write('MQTT%4s' % 'OK' if ha.is_connected() else 'ERR'))
    
    if ha.is_connected():
        ha.publish_state()
        print('Done.')
        break

    else:
        print('Not connected!')
        status_led.on()
        sleep(5)

## Deep Sleep ##

sleep(10)

status_led.off()
oled.power_off()

print('Sleep for %d min...' % config.SLEEP_FOR)
## https://docs.micropython.org/en/latest/library/esp.html#esp.deepsleep
## Note, GPIO pin 16 (or D0 on the Wemos D1 Mini) must be wired to the Reset pin. See README
## Note: ESP8266 only - use machine.deepsleep() on ESP32
## https://docs.micropython.org/en/latest/esp8266/tutorial/powerctrl.html#deep-sleep-mode

deepsleep(config.SLEEP_FOR * 60 * 1000000) 
