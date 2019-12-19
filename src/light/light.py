from lib.esp8266.wemos.d1mini import status_led
from lib.pwm_pin import PWMPin
import config

class Light():
    def __init__(self, state):
        self.pwm = PWMPin(config.LIGHT_GPIO, status_led=status_led)
        self.pwm.off()

    def on_light_on(self, state):
        if config.BATTERY_LOW_DISABLE == None or state.battery > config.BATTERY_LOW_DISABLE:
            self.pwm.on()

    def on_light_off(self, state):
        self.pwm.off()

    def on_brightness_change(self, state):
        self.pwm.set_duty_percent(state.brightness)

    def deinit(self):
        self.pwm.off()
