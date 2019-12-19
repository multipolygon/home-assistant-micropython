from lib.button import Button
import config

class MotionDetector():
    def __init__(self, state):
        def pir_on(*_):
            state.set(motion = True)

        def pir_off(*_):
            state.set(motion = False)

        Button(config.PIR_SENSOR_PIN, pir_on, pir_off, inverted=config.PIR_INVERTED)

