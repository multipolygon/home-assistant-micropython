from machine import Pin, PWM
from machine import Timer

class PWMPin():
    def __init__(self, gpio, pwm_enabled=True, off_delay=None, off_delay_callback=None, status_led=None):
        ## Relay default is D1
        self.pin = Pin(gpio, mode=Pin.OUT)
        self.pwm_enabled = pwm_enabled
        if self.pwm_enabled:
            self.pwm = PWM(self.pin, freq=1000)
        self.pwm_duty = 1024
        self.state = False
        self.off_delay = off_delay
        self.off_delay_callback = off_delay_callback
        self.timer = Timer(-1)
        self.status_led = status_led
        
    def set_duty(self, i):
        self.pwm_duty = i

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
            self.pwm.duty(self.pwm_duty)
        else:
            self.pin.on()
        if self.off_delay:
            self.timer.deinit()
            def callback(_):
                print('Off Delay Timer Callback')
                self.off()
                if self.off_delay_callback:
                    self.off_delay_callback()
            self.timer.init(
                period=self.off_delay * 1000,
                mode=Timer.ONE_SHOT,
                callback=callback
            )

    def off(self):
        self.state = False
        if self.status_led:
            self.status_led.off()
        if self.pwm_enabled:
            self.pwm.deinit()
        self.pin.off()
        if self.off_delay:
            self.timer.deinit()

    def toggle(self):
        if self.state:
            self.off()
        else:
            self.on()

    def set_off_delay(self, delay, callback):
        self.off_delay = delay
        self.off_delay_callback = callback
        
