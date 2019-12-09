from machine import Pin
from machine import Timer

class Button():
    def __init__(self, gpio, on_callback=None, off_callback=None, timeout_ms=1500, inverted=False):
        self.enabled = True
        self.pin = Pin(gpio, mode=Pin.IN)
        self.timer = Timer(-1)

        def timeout(*_):
            self.enabled = True
            if off_callback:
                off_callback()

        def handler(pin):
            self.timer.deinit()
            if pin.value() == (1 if not(inverted) else 0):
                if self.enabled:
                    self.enabled = False
                    if on_callback:
                        on_callback()
            else:
                self.timer.init(
                    period=timeout_ms,
                    mode=Timer.ONE_SHOT,
                    callback=timeout
                )

        self.pin.irq(
            trigger=Pin.IRQ_RISING|Pin.IRQ_FALLING,
            handler=handler
        )
