from lib.button import Button
from machine import Timer
from micropython import schedule
import battery
import config

class MotionDetector():
    def __init__(self, state):
        timer = Timer(-1)

        def timeout(*_):
            print('MotionDetector.timeout()')
            state.set(light = False)

        def _timeout(*_):
            schedule(timeout, None)
        
        def pir_on(*_):
            timer.deinit()
            if state.automatic_mode and not(state.manual_override) and (config.LOW_BATTERY_DISABLE == None or battery.percent() > config.LOW_BATTERY_DISABLE):
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
                    callback=_timeout
                )

        Button(config.PIR_SENSOR_PIN, pir_on, pir_off, inverted=config.PIR_INVERTED)

