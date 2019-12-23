from lib.home_assistant.mqtt import MQTT
from lib.home_assistant.switch import Switch
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

        valve = self.mqtt.add('Valve', Switch, icon = "mdi:water-pump")

        def set_valve(msg):
            state.set(valve_open = msg == valve.ON)

        self.mqtt.sub(valve.cmd_tpc(), set_valve)

        if config.BATT:
            battery = self.mqtt.add('Battery', Battery)

        status_led.fast_blink()
        state.mqtt = self.mqtt.try_pub_cfg()
        status_led.off()

        self._sched = False

        def pub_state(_):
            self._sched = False
            valve.set_state(state.valve_open)
            if config.BATT and hasattr(state, 'battery'):
                self.mqtt.set_attr('battery', state.battery)
                battery.set_state(state.battery)
            state.set(
                mqtt = self.mqtt.pub_state()
            )

        self.pub_state = pub_state

    def on_state_change(self, state, changed):
        if not self._sched:
            for i in ('valve_open', 'battery'):
                if i in changed:
                    self._sched = True
                    schedule(self.pub_state, None)
                    break

    def wait(self):
        self.mqtt.wait(led = status_led)

    def deinit(self):
        self.mqtt.discon()
