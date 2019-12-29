from machine import Pin
from micropython import schedule
from config import MOTN_GPIO, MOTN_VAL

class Motion():
    def __init__(self, state):
        self.pin = Pin(MOTN_GPIO, mode=Pin.IN)

    def start(self, state):
        def _cb(_):
            state.set(motion = state.enable and self.pin.value() == MOTN_VAL)

        def cb(pin):
            schedule(_cb, None)

        self.pin.irq(
            trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler = cb,
        )

    def stop(self, state):
        self.pin.irq(trigger=0)
