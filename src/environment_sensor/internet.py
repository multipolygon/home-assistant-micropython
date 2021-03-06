from home_assistant.mqtt import MQTT
from home_assistant.sensor import Sensor
import esp8266.wemos.d1mini.status_led as status_led
from micropython import schedule
from machine import reset_cause, DEEPSLEEP_RESET
from utime import sleep
import config
import secrets
import wifi

try:
    from uid import UID
except:
    UID = None

class Internet():
    def __init__(self, state):
        print(wifi.uid())

        if reset_cause() != DEEPSLEEP_RESET:
            status_led.slow_blink()
        wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
        status_led.off()

        mqtt = MQTT(config.NAME, secrets, uid = UID)

        opt = dict(exp_aft = config.FREQ * 2.5)

        if 'temp' in state:
            from home_assistant.sensors.temperature import Temperature
            mqtt.add('Temp', Temperature, **opt).set_state(state['temp'])

        if 'humid' in state:
            from home_assistant.sensors.humidity import Humidity
            mqtt.add('Humid', Humidity, **opt).set_state(state['humid'])

        if 'lux' in state:
            from home_assistant.sensors.illuminance import Illuminance
            mqtt.add('Lux', Illuminance, **opt).set_state(state['lux'])

        if 'analog' in state:
            mqtt.add('Analog', Sensor, unit = "%", icon = "mdi:gauge", **opt).set_state(state['analog'])

        if 'battery' in state:
            from home_assistant.sensors.battery import Battery
            mqtt.add('Battery', Battery, key = 'bat', **opt).set_state(state['battery'])
            mqtt.set_attr('battery', state['battery'])

        mqtt.set_attr("freq", config.FREQ)

        if wifi.is_connected():
            if reset_cause() != DEEPSLEEP_RESET:
                status_led.fast_blink()
            mqtt.connect()
            sleep(1)
            mqtt.pub_state()
            status_led.off()
            sleep(5)
            mqtt.discon()
            sleep(5)
