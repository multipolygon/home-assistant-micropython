from machine import Pin, PWM

class PWMPin():
    def __init__(self, gpio, pwm_enabled=True, status_led=None):
        self.pin = Pin(gpio, mode=Pin.OUT)
        self.pwm_enabled = pwm_enabled
        if self.pwm_enabled:
            self.pwm = PWM(self.pin, freq=1000)
        self.pwm_duty = 1024
        self.state = False
        self.status_led = status_led
        
    def set_duty(self, i):
        self.pwm_duty = i
        if self.is_on():
            self.on()

    def get_duty(self):
        return self.pwm_duty

    def set_duty_percent(self, i):
        self.set_duty(int(1024 / 100 * i))
        
    def get_duty_percent(self):
        return int(100 / 1024 * self.pwm_duty)

    def on(self):
        self.state = True
        if self.status_led:
            self.status_led.on()
        if self.pwm_enabled:
            if self.pwm_duty == 1024:
                self.pwm.deinit()
                self.pin.on()
            elif self.pwm_duty == 0:
                self.pwm.deinit()
                self.pin.off()
            else:
                self.pwm.duty(self.pwm_duty)
        else:
            self.pin.on()

    def off(self):
        self.state = False
        if self.status_led:
            self.status_led.off()
        if self.pwm_enabled:
            self.pwm.deinit()
        self.pin.off()

    def toggle(self):
        if self.state:
            self.off()
        else:
            self.on()

    def is_on(self):
        return self.state
    
    def is_off(self):
        return not(self.state)
