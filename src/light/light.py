from pwm import PWM
from config import GPIO, BRIGHTNESS, BATT
import config

class Light():
    def __init__(self, hub):
        self.update_on = ('light', 'brightness')
        self.pwm = PWM(GPIO, pwm = BRIGHTNESS)
        if hub.light:
            self.pwm.on()
        else:
            self.pwm.off()

    def update(self, hub, changed):
        if hub.light:
            if BATT == False or config.BATT_LOW == None or hub.battery > config.BATT_LOW:
                self.pwm.set_duty(hub.brightness)
                self.pwm.on()
        else:
            self.pwm.off()

    def stop(self, hub):
        self.pwm.off()
