from home_assistant.mqtt import MQTT
from home_assistant.switch import Switch
from home_assistant.sensors.battery import Battery
from home_assistant.binary_sensors.problem import Problem
import esp8266.wemos.d1mini.status_led as status_led
from utime import sleep, localtime
from uid import UID
import config
import secrets
import wifi

class Internet():
    def __init__(self, hub):
        pass
    
    def start(self, hub):
        if hub.trigger or localtime()[4] == 0:
            status_led.slow_blink()
            wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
            status_led.off()

            if wifi.is_connected():
                self.mqtt = MQTT(config.NAME, secrets, uid = UID)

                self.mqtt.add('', Problem, key = 'trig', exp_aft = config.NORMAL_SLEEP).set_state(hub.trigger)

                enable = self.mqtt.add('Enable', Switch)

                def enable_rx(msg):
                    hub.set(enable = msg == enable.ON)

                self.mqtt.sub(enable.cmd_tpc(), enable_rx)
                
                # self.mqtt.add('Battery', Battery, key = 'bat', exp_aft = 24 * 60 * 60).set_state(hub.battery)

                self.mqtt.set_attr('battery', hub.battery)
                self.mqtt.set_attr('rssi', wifi.rssi())

                status_led.fast_blink()
                self.mqtt.try_pub_cfg()
                sleep(1)
                self.mqtt.pub_state()
                status_led.off()

    def run(self, state):
        if hasattr(self, 'mqtt'):
            self.mqtt.wait()
                
    def stop(self, state):
        if hasattr(self, 'mqtt'):
            self.mqtt.discon()
            status_led.off()