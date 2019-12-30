from home_assistant.mqtt import MQTT
from home_assistant.light import Light
from home_assistant.switch import Switch
from home_assistant.binary_sensors.motion import Motion
from home_assistant.sensors.battery import Battery
from esp8266.wemos.d1mini import status_led
import wifi
import config
import secrets
from micropython import schedule

LIGHT = 'light'
SWITCH = 'switch'
AUTO = 'auto'
MOTN = 'motion'
BATT = 'battery'
BRI = 'brightness'
EN = 'enable'

def t(s):
    return s[0].upper() + s[1:]

class Internet():
    def __init__(self, state):
        self.update_on = set()
        
        print(wifi.uid())

        status_led.slow_blink()
        wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
        status_led.off()

        self.mqtt = MQTT(config.NAME, secrets)

        if config.COMPNT != None:
            self.update_on.add(LIGHT)
            
            if config.COMPNT == LIGHT:
                light = self.mqtt.add(t(LIGHT), Light, bri = config.BRIGHTNESS)
                
                if config.BRIGHTNESS:
                    def bri_rx(msg):
                        state.set(brightness = round(float(msg)))

                    self.mqtt.sub(light.bri_cmd_tpc(), bri_rx)
                
            elif config.COMPNT == SWITCH:
                light = self.mqtt.add(t(SWITCH), Switch)

            def light_rx(msg):
                state.set(light = msg == light.ON)

            self.mqtt.sub(light.cmd_tpc(), light_rx)

        if config.MOTN:
            self.update_on.add(MOTN)
            motion = self.mqtt.add(t(MOTN), Motion)
            enable = self.mqtt.add(t(EN), Switch)

            def enable_rx(msg):
                state.set(enable = msg == enable.ON)

            self.mqtt.sub(enable.cmd_tpc(), enable_rx)

            if config.COMPNT != None:
                auto = self.mqtt.add(t(AUTO), Switch)

                def auto_rx(msg):
                    state.set(auto = msg == auto.ON)

                self.mqtt.sub(auto.cmd_tpc(), auto_rx)

        if config.BATT:
            self.update_on.add(BATT + '_level')
            
            battery = self.mqtt.add(t(BATT), Battery)

        status_led.fast_blink()
        if config.BATT and config.BATT_LOW and state.battery < config.BATT_LOW:
            self.mqtt.do_pub_cfg = False
            self.mqtt.connect()
        else:
            self.mqtt.try_pub_cfg()
        status_led.off()

        self._sched = False

        def pub(_):
            self._sched = False
            if config.COMPNT != None:
                light.set_state(state.light)
                if config.COMPNT == LIGHT and config.BRIGHTNESS:
                    light.set_bri(state.brightness)
            if config.MOTN:
                motion.set_state(state.motion)
                enable.set_state(state.enable)
                if config.COMPNT != None:
                    auto.set_state(state.auto)
            if config.BATT:
                battery.set_state(state.battery)
                self.mqtt.set_attr(BATT, state.battery)
            self.mqtt.pub_state()

        self.pub = pub

    def start(self, state):
        self.pub(0)

    def run(self, state):
        self.mqtt.wait()

    def update(self, state, changed):
        if not self._sched:
            self._sched = True
            schedule(self.pub, None)

    def stop(self, state):
        self.mqtt.discon()
