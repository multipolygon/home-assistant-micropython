from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.mqtt import HomeAssistantMQTT
from lib.home_assistant.sensor import Sensor
from lib.home_assistant.sensors.battery import BatterySensor
from lib.home_assistant.sensors.humidity import HumiditySensor
from lib.home_assistant.sensors.illuminance import IlluminanceSensor
from lib.home_assistant.sensors.temperature import TemperatureSensor
from micropython import schedule
from machine import reset_cause, DEEPSLEEP_RESET
from utime import sleep
import config
import secrets
import wifi

class Internet():
    def __init__(self, state):
        print(HomeAssistant.UID)

        if reset_cause() != DEEPSLEEP_RESET:
            status_led.slow_blink()
        wifi.disable_access_point()
        wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
        status_led.off()

        HomeAssistant.NAME = config.NAME
        HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

        self.ha = ha = HomeAssistantMQTT(secrets)

        ha.set_attr("Interval", config.INTERVAL)

        opt = { 'expire_after': config.INTERVAL * 2.5 }

        if 'temperature' in state:
            ha.register('Temp', TemperatureSensor, **opt).set_state(state['temperature'])

        if 'humidity' in state:
            ha.register('Humid', HumiditySensor, **opt).set_state(state['humidity'])

        if 'illuminance' in state:
            ha.register('Lux', IlluminanceSensor, **opt).set_state(state['illuminance'])

        if 'analog' in state:
            ha.register('Analog', Sensor, unit = "%", icon = "mdi:gauge", **opt).set_state(state['analog'])

        if 'battery' in state:
            ha.set_attr('battery', '%d%%' % state['battery'])
            if config.BATTERY_SENSOR:
                ha.register('Battery', BatterySensor, key = 'bat', **opt).set_state(state['battery'])

        if wifi.is_connected():
            if reset_cause() != DEEPSLEEP_RESET:
                status_led.fast_blink()
            else:
                ha.publish_config_on_connect = False
            ha.mqtt_connect()
            ha.publish_state()
            status_led.off()
            sleep(5)
            self.ha.mqtt_disconnect()
