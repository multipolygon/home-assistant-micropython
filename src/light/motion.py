from machine import Pin
from micropython import schedule
from config import MOTN_GPIO, MOTN_VAL

class Motion():
    def __init__(self, hub):
        self.pin = Pin(MOTN_GPIO, mode=Pin.IN)
        self._sched = False

    def start(self, hub):
        def _cb(_):
            self._sched = False
            hub.set(motion = hub.enable and self.pin.value() == MOTN_VAL)

        def cb(pin):
            if not self._sched:
                self._sched = True
                schedule(_cb, None)

        self.pin.irq(
            trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler = cb,
        )

    def stop(self, hub):
        self.pin.irq(trigger=0)
