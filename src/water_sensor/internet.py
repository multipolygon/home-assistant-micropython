from home_assistant.binary_sensors.moisture import Moisture
from home_assistant.mqtt import MQTT
from home_assistant.sensors.battery import Battery
from home_assistant.switch import Switch
from machine import reset_cause, DEEPSLEEP_RESET
from uid import UID
from utime import sleep, localtime
import config
import esp8266.wemos.d1mini.status_led as status_led
import secrets
import wifi

class Internet():
    def __init__(self, hub):
        # Note, ESP8266 chip real-time clock will overflow every 7h45m
        hour = localtime()[3]
        print('hour', hour)
        self.do_pub_cfg = hour == 0 or reset_cause() != DEEPSLEEP_RESET
        print('do_pub_cfg', self.do_pub_cfg)
        hub.internet = hub.get('internet') or hub.water or self.do_pub_cfg
    
    def start(self, hub):
        if hub.internet:
            status_led.fast_blink()
            wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
            status_led.off()
            sleep(2)

            if wifi.is_connected():
                status_led.fast_blink()
                
                self.mqtt = MQTT(config.NAME, secrets, uid = UID)

                self.mqtt.add('Water', Moisture, prim = True, key = 'water', off_dly = config.NORMAL_SLEEP).set_state(hub.water)

                enable = self.mqtt.add('Enable', Switch, icon = "mdi:bell")

                def enable_rx(msg):
                    hub.set(enable = msg == enable.ON)

                self.mqtt.sub(enable.cmd_tpc(), enable_rx)
                
                self.mqtt.add('Battery', Battery, key = 'bat').set_state(hub.battery)

                self.mqtt.set_attr('battery', hub.battery)
                self.mqtt.set_attr('rssi', wifi.rssi())

                self.mqtt.do_pub_cfg = self.do_pub_cfg
                self.mqtt.connect()
                sleep(1)
                self.mqtt.pub_state()
                sleep(1)
                status_led.off()

    def run(self, hub):
        if hub.water:
            status_led.slow_blink()
        else:
            status_led.off()

        if hasattr(self, 'mqtt'):
            self.mqtt.wait()
                
    def stop(self, hub):
        if hasattr(self, 'mqtt'):
            self.mqtt.discon()
        wifi.disconnect()
        status_led.off()
