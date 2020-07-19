from machine import Pin, PWM
from utime import sleep_ms

class StatusLED():
    def __init__(self, gpio=2):
        self.led = Pin(gpio, Pin.OUT)
        self.pwm = PWM(self.led)

    def on(self):
        self.pwm.deinit()
        self.led.off()
        sleep_ms(200)
        self.led.off()

    def off(self):
        self.pwm.deinit()
        self.led.on()
        sleep_ms(200)
        self.led.on()

    def invert(self):
        self.pwm.deinit()
        self.led.value(not led.value())

    def set(self, state):
        if state:
            self.on()
        else:
            self.off()

    def slow_blink(self):
        self.pwm.freq(1)
        self.pwm.duty(512)

    def fast_blink(self):
        self.pwm.freq(3)
        self.pwm.duty(512)
