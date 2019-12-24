from lib.esp8266.wemos.d1mini import status_led
from machine import Pin
import config
from esp import deepsleep
from utime import sleep, sleep_ms
from micropython import schedule

class BallValve():
    def __init__(self, state):
        self.motor = Pin(config.MOTOR_GPIO, mode=Pin.OUT)
        self.contact = Pin(config.CONTACT_GPIO, mode=Pin.IN)
        state.valve_open = False
        self.rotate(False)

    def rotate(self, valve_open):
        status_led.fast_blink()
        while valve_open != (self.contact.value() == config.VALVE_OPEN_VAL):
            self.motor.on()
            sleep_ms(10)
        self.motor.off()
        if valve_open:
            status_led.on()
        else:
            status_led.off()

    def on_valve_open_change(self, state):
        if state.valve_open and self.battery_is_low(state.battery):
            status_led.slow_blink()
        else:
            self.rotate(state.valve_open)
            
    def battery_is_low(self, val):
        return config.BATT and config.BATT_LOW != None and val < config.BATT_LOW

    def check_battery(self, state):
        if self.battery_is_low(state.battery):
            print('Batt low!')
            state.set(valve_open = False)
            if config.BATT_LOW_SLEEP != None:
                def cb(_):
                    print('Deep sleep: %s sec' % config.BATT_LOW_SLEEP)
                    sleep(2)
                    state.stop()
                    sleep(2)
                    deepsleep(config.BATT_LOW_SLEEP * 1000000)
                    sleep(2)
                ## Schedule gives mqtt a chance to publish state:
                schedule(cb, None)
                return True
        return False

    def on_battery_change(self, state):
        self.check_battery(state)
