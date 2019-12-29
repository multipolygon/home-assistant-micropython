from lib.esp8266.wemos.d1mini import status_led
from lib.pwm import PWM
from config import GPIO, BRIGHTNESS, BATT, BATT_LOW

class Light():
    def __init__(self, state):
        self.update_on = ('light', 'brightness')
        self.pwm = PWM(GPIO, pwm = BRIGHTNESS, led = status_led)
        self.pwm.off()

    def update(self, state, changed):
        if state.light:
            if BATT == False or BATT_LOW == None or state.battery > BATT_LOW:
                self.pwm.set_duty(state.brightness)
                self.pwm.on()
        else:
            self.pwm.off()

    def stop(self, state):
        self.pwm.off()
