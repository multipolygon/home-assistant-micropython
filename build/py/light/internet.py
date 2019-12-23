from lib.home_assistant.mqtt import MQTT
from lib.home_assistant.light import Light
from lib.home_assistant.switch import Switch
from lib.home_assistant.binary_sensors.motion import Motion
from lib.home_assistant.sensors.battery import Battery
from lib.esp8266.wemos.d1mini import status_led
import wifi
import config
import secrets
from micropython import schedule

class Internet():
    def __init__(self, state):
        print(wifi.uid())

        status_led.slow_blink()
        wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
        status_led.off()

        self.mqtt = MQTT(config.NAME, secrets)

        if config.COMPNT != None:
            if config.COMPNT == 'Light':
                light = self.mqtt.add(config.COMPNT, Light, bri = config.BRIGHTNESS)
                
                if config.BRIGHTNESS:
                    def bri_rx(message):
                        state.set(brightness = round(float(message)))

                    self.mqtt.sub(light.bri_cmd_tpc(), bri_rx)
                
            elif config.COMPNT == 'Switch':
                light = self.mqtt.add(config.COMPNT, Switch)

            def light_rx(msg):
                state.set(light = msg == light.ON)

            self.mqtt.sub(light.cmd_tpc(), light_rx)

        if config.MOTN:
            motion = self.mqtt.add('Motion', Motion)

            if config.COMPNT != None:
                auto = self.mqtt.add('Auto', Switch)

                def auto_rx(message):
                    state.set(auto = message == auto.ON)

                self.mqtt.sub(auto.cmd_tpc(), auto_rx)

        if config.BATT:
            battery = self.mqtt.add('Battery', Battery)

        status_led.fast_blink()
        state.telemetry = self.mqtt.try_pub_cfg()
        status_led.off()

        self.pub_sched = False

        def pub_state(_):
            self.pub_sched = False
            if config.COMPNT != None:
                light.set_state(state.light)
                if config.COMPNT == 'light' and config.BRIGHTNESS:
                    light.set_bri(state.brightness)
            if config.MOTN:
                motion.set_state(state.motion and state.auto)
                if config.COMPNT != None:
                    auto.set_state(state.auto)
            if config.BATT:
                battery.set_state(state.battery)
                self.mqtt.set_attr('battery', state.battery)
            state.set(
                telemetry = self.mqtt.pub_state()
            )

        self.pub_state = pub_state

    def sched_pub_state(self):
        if not self.pub_sched:
            self.pub_sched = True
            schedule(self.pub_state, None)

    def on_auto_change(self, state):
        self.sched_pub_state()

    def on_battery_level_change(self, state):
        self.sched_pub_state()

    def on_light_change(self, state):
        if config.COMPNT != None:
            self.sched_pub_state()

    def on_motion_change(self, state):
        if state.auto:
            self.sched_pub_state()

    def wait(self):
        self.mqtt.wait()

    def deinit(self):
        self.mqtt.discon()
