import esp8266.wemos.d1mini.status_led as status_led
from machine import Pin
import config

class Pump():
    def __init__(self, state):
        self.update_on = ('pump')
        self.pin = Pin(config.PUMP_GPIO, mode=Pin.OUT)
        self.pin.value(config.PUMP_OFF)
        status_led.off()

    def update(self, state, changed):
        status_led.led.value(state.pump == config.PUMP_ON)
        status_led.on() if state.pump == config.PUMP_ON else status_led.off()

