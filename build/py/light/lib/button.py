from machine import Pin
from machine import Timer
from micropython import schedule

class Button():
    def __init__(self, gpio, on_callback=None, off_callback=None, timeout_ms=1500, on_value=1):
        self.enabled = True
        self.pin = Pin(gpio, mode=Pin.IN)
        self.timer = Timer(-1)

        def timeout(_):
            self.enabled = True
            if off_callback:
                schedule(off_callback, None)

        def handler(pin):
            self.timer.deinit()
            if pin.value() == on_value:
                if self.enabled:
                    self.enabled = False
                    if on_callback:
                        schedule(on_callback, None)
            else:
                self.timer.init(
                    period=timeout_ms,
                    mode=Timer.ONE_SHOT,
                    callback=timeout
                )

        self.pin.irq(handler=handler, trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING)

    def deinit(self):
        self.pin.irq(trigger=0)
        self.timer.deinit()
