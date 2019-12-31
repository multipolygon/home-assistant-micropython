import esp8266.wemos.d1mini.status_led as status_led
from machine import Pin
import config
from esp import deepsleep
from utime import sleep, sleep_ms
from micropython import schedule

class BallValve():
    def __init__(self, state):
        self.update_on = ('valve_open', 'battery')
        self.motor = Pin(config.MOTOR_GPIO, mode=Pin.OUT)
        self.contact = Pin(config.CONTACT_GPIO, mode=Pin.IN)
        state.valve_open = False
        self.rotate(False)

    def rotate(self, valve_open):
        ## TODO: Use timer to turn off motor
        status_led.fast_blink()
        for i in range(1000): ## try for 10 sec
            if valve_open == (self.contact.value() == config.VALVE_OPEN_VAL):
                break
            self.motor.on()
            sleep_ms(10)
        self.motor.off()
        if valve_open:
            status_led.on()
        else:
            status_led.off()

    def update(self, state, changed):
        if 'battery' in changed:
            self.check_battery(state)

        if 'valve_open' in changed:
            if state.valve_open and self.battery_is_low(state):
                status_led.slow_blink()
            else:
                self.rotate(state.valve_open)
            
    def battery_is_low(self, state):
        return config.BATT and config.BATT_LOW != None and state.battery < config.BATT_LOW

    def check_battery(self, state):
        if self.battery_is_low(state):
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

