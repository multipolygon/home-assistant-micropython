from lib.esp8266.wemos.d1mini import status_led
from machine import Pin
import config

class Pump():
    def __init__(self, state):
        self.pin = Pin(config.PUMP_GPIO, mode=Pin.OUT)
        self.pin.off()

    def on_pump_on(self, state):
        status_led.on()
        self.pin.on()

    def on_pump_off(self, state):
        status_led.off()
        self.pin.off()
