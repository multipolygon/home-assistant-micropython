from machine import Pin
from utime import ticks_ms, ticks_diff

class Button():
    def __init__(self, gpio, callback, delay_ms=1500, inverted=False):
        self.pin = Pin(gpio, mode=Pin.IN)
        self.ticks = ticks_ms()

        def handler(pin):
            ticks = self.ticks
            self.ticks = ticks_ms()
            if pin.value() == (1 if not(inverted) else 0) and ticks_diff(ticks_ms(), ticks) > delay_ms:
                callback()

        self.pin.irq(
            trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,
            handler=handler
        )
