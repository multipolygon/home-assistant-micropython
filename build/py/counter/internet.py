from home_assistant.mqtt import MQTT
from home_assistant.sensor import Sensor
from home_assistant.sensors.battery import Battery
import esp8266.wemos.d1mini.status_led as status_led
from micropython import schedule
import config
import secrets
import wifi

class Internet():
    def __init__(self, state):
        self.update_on = ('count', 'battery_level')
        
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

    def update(self, state, changed):
        if not self._sched:
            self.pub_sched = True
            schedule(self.pub_state, 0)

    def start(self, state):
        self.pub_state(0)

    def run(self, state):
        self.mqtt.wait(led = status_led)

    def stop(self, state):
        self.mqtt.discon()
