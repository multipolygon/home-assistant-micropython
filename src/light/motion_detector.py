from machine import Pin
import config

class MotionDetector():
    def __init__(self, state):
        self.pin = Pin(config.MOTION_SENSOR_GPIO, mode=Pin.IN)

        def handler(pin):
            state.set(motion = pin.value() == config.MOTION_DETECTED_VALUE)

        self.pin.irq(handler=handler, trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING)

    def deinit(self):
        self.pin.irq(trigger=0)
