from machine import Pin
from machine import Timer
from micropython import schedule
import config

class Counter():
    def __init__(self, state):
        self.state = state
        self.count = state.count = 0
        self.pin = Pin(config.GPIO, mode=Pin.IN)
        self.led = Pin(config.LED, Pin.OUT) if config.LED else None
        self.timer = Timer(-1)

    def start(self):
        def increment(_):
            self.count += 1
            if self.led:
                self.led.value(self.count % 2 == 0)
                
        self.pin.irq(
            trigger = Pin.IRQ_RISING if config.GPIO_VAL == 1 else Pin.IRQ_FALLING,
            handler = increment,
        )

        def reset(_):
            c = self.count
            self.count = 0
            self.state.set(count = c)

        def cb(_):
            schedule(reset, None)
        
        self.timer.init(
            period = config.FREQ * 1000,
            callback = cb,
        )

    def stop(self):
        self.pin.irq(trigger=0)
        self.timer.deinit()
