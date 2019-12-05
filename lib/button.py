from machine import Pin, Timer

class Button():
    def __init__(self, gpio, callback, delay_ms=500, inverted=False):
        self.pin = Pin(gpio, mode=Pin.IN)

        self.enable = True
        self.timer = Timer(-1)

        def press():
            self.timer.deinit()
            if self.enable:
                self.enable = False
                callback()

        def reenable(_):
            self.enable = True

        def release():
            self.timer.deinit()
            self.timer.init(
                mode=Timer.ONE_SHOT,
                period=delay_ms,
                callback=reenable
            )

        def handler(pin):
            if pin.value() == (1 if not(inverted) else 0):
                press()
            else:
                release()

        self.pin.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler=handler
        )
