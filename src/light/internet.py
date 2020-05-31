from home_assistant.mqtt import MQTT
from home_assistant.light import Light
from home_assistant.switch import Switch
from home_assistant.binary_sensors.motion import Motion
from home_assistant.sensors.battery import Battery
from status_led import StatusLED
import wifi
import config
import secrets
from micropython import schedule

try:
    from uid import UID
except:
    UID = None

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
    def __init__(self, hub):
        self.update_on = set()
        led = StatusLED(gpio=config.LED_GPIO)
        wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD, led=led)
        self.mqtt = MQTT(config.NAME, secrets, uid = UID, led=led)

        if config.COMPNT != None:
            self.update_on.add(LIGHT)

            if config.COMPNT == LIGHT:
                light = self.mqtt.add(t(LIGHT), Light, prim = True, bri = config.BRIGHTNESS)
                
                if config.BRIGHTNESS:
                    def bri_rx(msg):
                        hub.set(brightness = round(float(msg)))

                    self.mqtt.sub(light.bri_cmd_tpc(), bri_rx)
                
            elif config.COMPNT == SWITCH:
                light = self.mqtt.add(t(SWITCH), Switch, prim = True)

            else:
                print('ERR', COMPNT);

            self.mqtt.sub_dev_cmd(light.compnt_base_tpc())

            def light_rx(msg):
                hub.set(light = msg == light.ON)

            self.mqtt.sub(light.cmd_tpc(), light_rx)

        if config.MOTN:
            self.update_on.add(MOTN)
            motion = self.mqtt.add(t(MOTN), Motion)
            enable = self.mqtt.add(t(EN), Switch)

            def enable_rx(msg):
                hub.set(enable = msg == enable.ON)

            self.mqtt.sub(enable.cmd_tpc(), enable_rx)

            if config.COMPNT != None:
                auto = self.mqtt.add(t(AUTO), Switch)

                def auto_rx(msg):
                    hub.set(auto = msg == auto.ON)

                self.mqtt.sub(auto.cmd_tpc(), auto_rx)

        if config.BATT:
            self.update_on.add(BATT + '_level')
            
            battery = self.mqtt.add(t(BATT), Battery)

        self.mqtt.try_pub_cfg()

        self._sched = False

        def pub(_):
            self._sched = False
            if config.COMPNT != None:
                if hub.light_cmd:
                    hub.light_cmd = False
                    try:
                        self.mqtt.publish(light.cmd_tpc(), light.ON if hub.light else light.OFF, retain = True)
                    except:
                        pass
                light.set_state(hub.light)
                if config.COMPNT == LIGHT and config.BRIGHTNESS:
                    light.set_bri(hub.brightness)
            if config.MOTN:
                motion.set_state(hub.motion)
                enable.set_state(hub.enable)
                if config.COMPNT != None:
                    auto.set_state(hub.auto)
            if config.BATT:
                battery.set_state(hub.battery)
                self.mqtt.set_attr(BATT, hub.battery)
            if wifi.is_connected():
                self.mqtt.set_attr('rssi', wifi.rssi())
            self.mqtt.pub_state()

        self.pub = pub

    def start(self, hub):
        self.pub(0)

    def run(self, hub):
        self.mqtt.wait()

    def update(self, hub, changed):
        if not self._sched:
            self._sched = True
            schedule(self.pub, None)

    def stop(self, hub):
        self.mqtt.discon()
