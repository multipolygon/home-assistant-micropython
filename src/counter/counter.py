from machine import Pin
from machine import Timer
from micropython import schedule
import config

class Counter():
    def __init__(self, state):
        self.state = state
        self.count = 0
        self.pin = Pin(config.GPIO, mode=Pin.IN)
        self.timer = Timer(-1)

        self.state.set(count = 0)

        def increment(pin):
            self.count += 1

        self.pin.irq(
            trigger = Pin.IRQ_RISING if config.GPIO_VALUE == 1 else Pin.IRQ_FALLING,
            handler = increment,
        )

        def reset(_):
            self.state.set(count = self.count)
            self.count = 0

        def interval(_):
            schedule(reset, None)
        
        self.timer.init(
            period = config.INTERVAL * 1000,
            callback = interval,
        )

    def deinit(self):
        self.pin.irq(trigger=0)
        self.timer.deinit()
