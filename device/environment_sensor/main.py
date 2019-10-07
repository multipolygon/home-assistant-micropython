from machine import ADC, Pin, I2C
from utime import sleep
import esp
import gc
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led
from lib.esp8266.wemos.d1mini import oled
from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.sht30.sht30 import SHT30
from lib.esp8266.bh1750.bh1750 import BH1750
from lib.home_assistant.binary_sensors.connectivity import ConnectivityBinarySensor
from lib.home_assistant.sensors.signal_strength import SignalStrengthSensor
from lib.home_assistant.sensors.temperature import TemperatureSensor
from lib.home_assistant.sensors.humidity import HumiditySensor
from lib.home_assistant.sensors.illuminance import IlluminanceSensor
from lib.home_assistant.sensor import Sensor

def read_temperature_humidity_sensor():
    sht30 = SHT30(scl_pin = pinmap.SCL, sda_pin = pinmap.SDA)
    if sht30.is_present():
        return sht30.measure()
    else:
        return (0, 0)

def read_light_sensor():
    i2c = I2C(scl=Pin(pinmap.SCL), sda=Pin(pinmap.SDA))
    bh1750 = BH1750(i2c)
    if bh1750.is_present():
        lux = bh1750.luminance(BH1750.ONCE_HIRES_1)
        bh1750.off()
        return lux
    else:
        return 0

def read_adc():
    return ADC(pinmap.A0).read()
    
status_led.off()
oled.write('POWER ON')

# print('Read DHT sensor...')
temperature, humidity = read_temperature_humidity_sensor()
# print('Read light sensor...')
light_level = read_light_sensor()
# print('Read ADC...')
adc_reading = read_adc()

oled.write('%4.0f%4.0f' % (temperature, humidity))
oled.write('%7.1f' % (light_level))
oled.write('%8d' % (adc_reading))

gc.collect()

# print('MQTT...')
mqtt = MQTTClient(
    wifi.mac(),
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

# print('MQTT connecting...')
mqtt.connect()
oled.write('%4s%4s' % (wifi.is_connected() and wifi.rssi() or 'Err', mqtt.is_connected() and 'OK' or 'Err'))

sleep_for = 15 # minutes

if mqtt.is_connected():
    state = {} ## State is a 'global' object containing all sensor data

    # print('Initialise sensors...')
    status_sensor = ConnectivityBinarySensor("Status", state, secrets.MQTT_USER)
    wifi_signal_sensor = SignalStrengthSensor("WiFi Signal Strength", state, secrets.MQTT_USER)
    temperature_sensor = TemperatureSensor(None, state, secrets.MQTT_USER)
    humidity_sensor = HumiditySensor(None, state, secrets.MQTT_USER)
    illuminance_sensor = IlluminanceSensor(None, state, secrets.MQTT_USER)
    analogue_sensor = Sensor('Analogue', state, secrets.MQTT_USER)
    
    # print('MQTT send config...')
    mqtt.publish_json(status_sensor.config_topic(), status_sensor.config(off_delay=sleep_for*60+60), retain=True)
    gc.collect()
    mqtt.publish_json(wifi_signal_sensor.config_topic(), wifi_signal_sensor.config(expire_after=sleep_for*60+60), retain=True)
    gc.collect()
    mqtt.publish_json(temperature_sensor.config_topic(), temperature_sensor.config(expire_after=sleep_for*60+60), retain=True)
    gc.collect()
    mqtt.publish_json(humidity_sensor.config_topic(), humidity_sensor.config(expire_after=sleep_for*60+60), retain=True)
    gc.collect()
    mqtt.publish_json(illuminance_sensor.config_topic(), illuminance_sensor.config(expire_after=sleep_for*60+60), retain=True)
    gc.collect()
    mqtt.publish_json(analogue_sensor.config_topic(), analogue_sensor.config(expire_after=sleep_for*60+60), retain=True)
    gc.collect()

    # print('Set state...')
    status_sensor.set_state(True)
    status_sensor.set_attributes({ "ip": wifi.ip(), "mac": wifi.mac() })
    wifi_signal_sensor.set_state(wifi.rssi())
    temperature_sensor.set_state(round(temperature, 2))
    humidity_sensor.set_state(round(humidity, 2))
    illuminance_sensor.set_state(round(light_level, 2))
    analogue_sensor.set_state(round(adc_reading, 2))

    # print('MQTT send state...')
    mqtt.publish_json(status_sensor.state_topic(), state) ## Note, all sensors share the same state topic.
    
    # print('Done.')
    
else:
    # print('Error, not connected!')
    status_led.on()

sleep(10)
status_led.off()

mqtt.disconnect()
wifi.disconnect()

print('deep sleeping for %d min...' % sleep_for)
## https://docs.micropython.org/en/latest/library/esp.html#esp.deepsleep
## Note, GPIO pin 16 (or D0 on the Wemos D1 Mini) must be wired to the Reset pin. See README
esp.deepsleep(sleep_for * 60 * 1000000)
