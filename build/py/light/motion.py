from machine import Pin
from micropython import schedule
import config

class Motion():
    def __init__(self, state):
        self.pin = Pin(config.MOTN_GPIO, mode=Pin.IN)

        def update(_):
            state.set(motion = self.pin.value() == config.MOTN_VAL)

        def handler(pin):
            schedule(update, None)

        self.pin.irq(
            handler = handler,
            trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING,
        )

    def deinit(self):
        self.pin.irq(trigger=0)
