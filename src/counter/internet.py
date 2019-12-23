from lib.home_assistant.mqtt import MQTT
from lib.home_assistant.sensor import Sensor
from lib.home_assistant.sensors.battery import Battery
from lib.esp8266.wemos.d1mini import status_led
from micropython import schedule
import config
import secrets
import wifi

class Internet():
    def __init__(self, state):
        print(wifi.uid())

        status_led.slow_blink()
        wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
        status_led.off()

        self.mqtt = MQTT(config.NAME, secrets)

        counter = self.mqtt.add(
            'Counter',
            Sensor,
            unit = config.UNIT,
            icon = 'mdi:counter',
        )

        if config.BATT:
            battery = self.mqtt.add('Battery', Battery)

        status_led.fast_blink()
        state.mqtt = self.mqtt.try_pub_cfg()
        status_led.off()

        self._sched = False

        def pub_state(_):
            status_led.on()
            self._sched = False
            counter.set_state(state.count)
            if config.BATT:
                battery.set_state(state.battery)
                counter.set_attr('battery', state.battery)
            state.set(
                mqtt = self.mqtt.pub_state()
            )
            status_led.off()

        self.pub_state = pub_state

    def on_state_change(self, state, changed):
        if not self._sched:
            for i in ('count', 'battery'):
                if i in changed:
                    self.pub_sched = True
                    schedule(self.pub_state, None)
                    break

    def wait(self):
        self.mqtt.wait(led = status_led)

    def deinit(self):
        self.mqtt.mqtt_discon()
