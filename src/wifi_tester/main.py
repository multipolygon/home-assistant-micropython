import esp
from utime import sleep

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import oled
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led

from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.sensors.signal_strength import SignalStrengthSensor

HomeAssistant.NAME = "Env Sensor"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

status_led.on()
oled.write('POWER ON')
oled.write('UID:')
print(oled.write(HomeAssistant.UID))
oled.write('WiFi:')
oled.write(secrets.WIFI_NAME)
sleep(2)

sensor = SignalStrengthSensor('RSSI')

mqtt = MQTTClient(
    wifi.mac(),
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

def publish_config():
    print('MQTT config...')
    mqtt.publish_json(sensor.config_topic(), sensor.config(expire_after=300), retain=True)
    print('Done.')

mqtt.set_connected_callback(publish_config)

mqtt.connect()

bling = "/\\"

for i in range(60):
    status_led.on()
    print(oled.write('%1s%7d' % (bling[i % 2], wifi.rssi())))
    sensor.set_state(wifi.rssi())
    sensor.set_attr({ "UID": HomeAssistant.UID, "IP": wifi.ip(), "MAC": wifi.mac() })
    mqtt.publish_json(sensor.state_topic(), sensor.state(), reconnect=True)
    status_led.off()
    sleep(4)

oled.power_off()
wifi.power_off()
esp.deepsleep()
