from machine import Pin
from machine import PWM as _PWM

class PWM():
    def __init__(self, gpio, pwm=True, led=None):
        self.ison = False
        self.pin = Pin(gpio, mode = Pin.OUT)
        self.duty = 100
        self.pwm = _PWM(self.pin, freq = 1000) if pwm else None
        self.led = led
        
    def set_duty(self, v):
        self.duty = v
        if self.ison:
            self.on()

    def on(self):
        self.ison = True
        if self.led:
            self.led.on()
        if self.pwm:
            if self.duty >= 100:
                self.pwm.deinit()
                self.pin.on()
            elif self.duty <= 0:
                self.pwm.deinit()
                self.pin.off()
            else:
                self.pwm.duty(round(10.24 * self.duty))
        else:
            self.pin.on()

    def off(self):
        self.ison = False
        if self.led:
            self.led.off()
        if self.pwm:
            self.pwm.deinit()
        self.pin.off()

