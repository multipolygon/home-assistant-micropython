from lib.esp8266.wemos.d1mini import status_led
from lib.pwm_pin import PWMPin
import config

class Light():
    def __init__(self, state):
        pwm = PWMPin(config.PWM_PIN, status_led=status_led)
        pwm.off()

        def update_light(state):
            print('update_light()')
            pwm.set_duty_percent(state.brightness)
            pwm.on() if state.light else pwm.off()

        state.set_callback(update_light, on=['light', 'brightness'])
