from lib.esp8266.wemos.d1mini import status_led
from machine import Pin
import config

class BallValve():
    def __init__(self, state):
        self.motor = Pin(config.MOTOR_GPIO, mode=Pin.OUT)
        self.contact = Pin(config.CONTACT_GPIO, mode=Pin.IN)
        self.rotate(False)

    def rotate(self, valve_open):
        status_led.fast_blink()
        while valve_open != (self.contact.value() == config.VALVE_OPEN_VAL):
            self.motor.on()
        self.motor.off()
        if valve_open:
            status_led.on()
        else:
            status_led.off()
            
    def battery_is_low(self, val):
        return config.BATT and config.BATT_LOW != None and val < config.BATT_LOW

    def on_valve_open_change(self, state):
        if state.valve_open and self.battery_is_low(state.battery):
            status_led.slow_blink()
        else:
            self.rotate(state.valve_open)

    def on_battery_change(self, state):
        if self.battery_is_low(state.battery):
            self.rotate(False)
