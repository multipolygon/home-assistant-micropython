from machine import Pin
from micropython import schedule
import config

class MotionDetector():
    def __init__(self, state):
        self.pin = Pin(config.MOTION_SENSOR_GPIO, mode=Pin.IN)

        def update(_):
            state.set(motion = self.pin.value() == config.MOTION_DETECTED_VALUE)

        def handler(pin):
            schedule(update, None)

        self.pin.irq(
            handler = handler,
            trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING,
        )

    def deinit(self):
        self.pin.irq(trigger=0)
