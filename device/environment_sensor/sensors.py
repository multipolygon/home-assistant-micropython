from machine import ADC, Pin, I2C
from utime import sleep
import esp
import pinmap
import status_led
import oled
import secrets
import wifi
from umqtt_robust import MQTTClient
import home_assistant
from sht30 import SHT30
from bh1750 import BH1750

status_led.on()
oled.write('POWER ON')

sleep_for = 15 # minutes

## DHT Sensor

print('Read DHT sensor...')

dht_sensor = SHT30(scl_pin = pinmap.SCL, sda_pin = pinmap.SDA)

if dht_sensor.is_present():
    temperature, humidity = dht_sensor.measure()
else:
    temperature, humidity = (0, 0)

oled.write('%4.0f%4.0f' % (temperature, humidity))

## Light Sensor

print('Read light sensor...')

i2c = I2C(scl=Pin(pinmap.SCL), sda=Pin(pinmap.SDA))
light_sensor = BH1750(i2c)

if light_sensor.is_present():
    light_level = light_sensor.luminance(BH1750.ONCE_HIRES_1)
    light_sensor.off()
else:
    light_level = 0

oled.write('%7.1f' % (light_level))

## ADC

print('Read ADC...')

adc = ADC(pinmap.A0)
adc_reading = adc.read()

oled.write('%8d' % (adc_reading))

## MQTT

mqtt = MQTTClient(
    bytearray(home_assistant.MODEL + home_assistant.UID),
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

def mqtt_connected_callback():
    print('MQTT sending config...')
    
    home_assistant.MAC = wifi.mac()
    home_assistant.TOPIC_PREFIX = secrets.MQTT_USER

    state = {}
    
    ha_status = home_assistant.ConnectivityBinarySensor("Status", state)
    ha_wifi_signal_strength = home_assistant.SignalStrengthSensor("WiFi Signal Strength", state)
    ha_temperature = home_assistant.TemperatureSensor(state=state)
    ha_humidity = home_assistant.HumiditySensor(state=state)
    ha_adc = home_assistant.GenericSensor('Analogue', state)
    
    mqtt.publish_json(ha_status.config_topic(), ha_status.config(off_delay=sleep_for*60+60), retain=True)
    mqtt.publish_json(ha_wifi_signal_strength.config_topic(), ha_wifi_signal_strength.config(expire_after=sleep_for*60+60), retain=True)
    mqtt.publish_json(ha_temperature.config_topic(), ha_temperature.config(expire_after=sleep_for*60+60), retain=True)
    mqtt.publish_json(ha_humidity.config_topic(), ha_humidity.config(expire_after=sleep_for*60+60), retain=True)
    mqtt.publish_json(ha_adc.config_topic(), ha_adc.config(expire_after=sleep_for*60+60), retain=True)

    ha_status.set_state(True)
    ha_status.set_attributes({ "ip_address": wifi.ip(), "mac_address": wifi.mac() })
    ha_wifi_signal_strength.set_state(wifi.rssi())
    ha_temperature.set_state(round(temperature, 2))
    ha_humidity.set_state(round(humidity, 2))
    ha_adc.set_state(round(adc_reading, 2))

    sleep(1)
    
    mqtt.publish_json(ha_status.state_topic(), state)
    
    print('MQTT config sent.')

mqtt.set_connected_callback(mqtt_connected_callback)

print('MQTT connecting...')
mqtt.connect()

oled.write('%4s%4s' % (wifi.is_connected() and wifi.rssi() or 'Err', mqtt.is_connected() and 'OK' or 'Err'))

sleep(10)
status_led.off()

mqtt.disconnect()
wifi.disconnect()

print('deep sleeping for %d min...' % sleep_for)
## https://docs.micropython.org/en/latest/library/esp.html#esp.deepsleep
## Note, GPIO pin 16 (or D0 on the Wemos D1 Mini) must be wired to the Reset pin. See README
esp.deepsleep(sleep_for * 60 * 1000000)
