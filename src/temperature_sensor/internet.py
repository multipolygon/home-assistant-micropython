from home_assistant.mqtt import MQTT
from home_assistant.sensor import Sensor
from home_assistant.sensors.temperature import Temperature
from home_assistant.sensors.humidity import Humidity
from status_led import StatusLED
from machine import reset_cause, DEEPSLEEP_RESET
from utime import sleep, ticks_us
import config
import secrets
import wifi

try:
    from uid import UID
except:
    UID = None

class Internet():
    def __init__(self, state):
        led = None if reset_cause() == DEEPSLEEP_RESET else StatusLED(config.LED)
            
        wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD, led=led)

        if wifi.is_connected():
            print(wifi.mac(), wifi.ip(), wifi.rssi())
            
            mqtt = MQTT(config.NAME, secrets, uid = UID, led=led)

            opt = dict(exp_aft = config.FREQ * 2.5)

            mqtt.add('Temp', Temperature, **opt).set_state(state['temp'])

            mqtt.add('Humid', Humidity, **opt).set_state(state['humid'])

            mqtt.set_attr("freq", config.FREQ)

            mqtt.do_pub_cfg = reset_cause() != DEEPSLEEP_RESET or ticks_us() % 10 == 0
        
            mqtt.connect()
            sleep(1)
            
            mqtt.pub_state()
            sleep(5)
            
            mqtt.discon()
            sleep(5)
