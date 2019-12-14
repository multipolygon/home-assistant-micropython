from lib.button import Button
from machine import Timer
from micropython import schedule
import config

class MotionDetector():
    def __init__(self, state):
        timer = Timer(-1)

        def _timeout(*_):
            print('timeout()')
            state.set(light = False)

        def timeout(*_):
            schedule(_timeout, None)
        
        def pir_on(*_):
            timer.deinit()
            if state.automatic_mode and not(state.manual_override):
                state.set(motion = True, light = True)
            else:
                state.set(motion = True)

        def pir_off(*_):
            timer.deinit()
            state.set(motion = False)
            if state.light and not(state.manual_override):
                timer.init(
                    period=config.MOTION_LIGHT_OFF_DELAY * 1000,
                    mode=Timer.ONE_SHOT,
                    callback=timeout
                )

        Button(config.PIR_SENSOR_PIN, pir_on, pir_off, inverted=config.PIR_INVERTED)

        def automatic_mode(state):
            print('automatic_mode()')
            if not(state.automatic_mode) and state.light and not(state.manual_override):
                timer.deinit()
                state.set(light = False)

        state.set_callback(automatic_mode, on=['automatic_mode'])
