from machine import Pin, PWM

class PWMPin():
    def __init__(self, gpio, pwm_enabled=True):
        ## Relay default is D1
        self.pin = Pin(gpio, mode=Pin.OUT)
        self.pwm_enabled = pwm_enabled
        if self.pwm_enabled:
            self.pwm = PWM(self.pin, freq=1000)
        self.pwm_duty = 1024
        self.state = False

    def duty(self, i):
        self.pwm_duty = i

    def on(self):
        self.state = True
        if self.pwm_enabled:
            self.pwm.duty(self.pwm_duty)
        else:
            self.pin.on()

    def off(self):
        self.state = False
        if self.pwm_enabled:
            self.pwm.deinit()
        self.pin.off()

    def toggle(self):
        if self.state:
            self.off()
        else:
            self.on()
