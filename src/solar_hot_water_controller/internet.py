from home_assistant.mqtt import MQTT
from home_assistant.climate import Climate, MODE_OFF, MODES
from home_assistant.sensors.temperature import Temperature
import esp8266.wemos.d1mini.status_led as status_led
from micropython import schedule
import wifi
import config
import secrets

class Internet():
    def __init__(self, state):
        self.update_on = ('mode', 'tank_target_temp', 'tank_temp', 'pump', 'solar_temp')
        
        print(wifi.uid())

        status_led.slow_blink()
        wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
        status_led.off()

        self.mqtt = MQTT(config.NAME, secrets)

        ctl = self.mqtt.add('Controller', Climate, key = 'ctl', max = config.TANK_MAX_TEMP)
        temp = self.mqtt.add('Solar', Temperature, key = 'sol')
        
        def set_mode(msg):
            if msg in MODES:
                state.set(mode = msg)

        self.mqtt.sub(ctl.mode_cmd_tpc(), set_mode)

        def set_targ(msg):
            state.set(tank_target_temp = round(float(msg)))

        self.mqtt.sub(ctl.targ_cmd_tpc(), set_targ)

        status_led.fast_blink()
        state.mqtt = self.mqtt.try_pub_cfg()
        status_led.off()

        self._sched = False

        def pub_state(_):
            self._sched = False
            ctl.set_mode(state.mode)
            ctl.set_targ(state.tank_target_temp)
            ctl.set_temp(state.tank_temp)
            ctl.set_actn('off' if state.mode == MODE_OFF else ('heating' if state.pump else 'idle'))
            temp.set_state(state.solar_temp)
            state.set(
                mqtt = self.mqtt.pub_state()
            )

        self.pub_state = pub_state

    def update(self, state, changed):
        if not self._sched:
            self._sched = True
            schedule(self.pub_state, 0)

    def start(self, state):
        self.pub_state(0)

    def run(self, state):
        self.mqtt.wait(led = status_led)

    def stop(self, state):
        self.mqtt.discon()
