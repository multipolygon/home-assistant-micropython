from home_assistant.mqtt import MQTT
from home_assistant.switch import Switch
from home_assistant.sensors.battery import Battery
import esp8266.wemos.d1mini.status_led as status_led
from micropython import schedule
from machine import reset_cause, DEEPSLEEP_RESET
import config
import secrets
import wifi

class Internet():
    def __init__(self, state):
        self.update_on = ('valve_open', 'battery_level')
        
        state.mqtt = False
        self.mqtt = MQTT(config.NAME, secrets)

        valve = self.mqtt.add(
            'Valve',
            Switch,
            opt = False, ## not optimistic
            ret = False, ## no retain
            icon = "mdi:water-pump",
        )

        def set_valve(msg):
            state.set(valve_open = msg == valve.ON)

        self.mqtt.sub(valve.cmd_tpc(), set_valve)

        if config.BATT:
            battery = self.mqtt.add('Battery', Battery)
            
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

    def update(self, state, changed):
        if not self._sched:
            self._sched = True
            schedule(self.pub_state, 0)

    def run(self, state):
        print(wifi.uid())
        status_led.slow_blink()
        wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
        status_led.fast_blink()
        if reset_cause() == DEEPSLEEP_RESET:
            self.mqtt.do_pub_cfg = False
            self.mqtt.connect()
        else:
            self.mqtt.try_pub_cfg()
        self.pub_state(None)
        status_led.off()
        self.mqtt.wait(led = status_led)

    def stop(self, state):
        self.mqtt.reconnect = False
        self.mqtt.discon()
