from machine import ADC
from machine import Timer
from micropython import schedule
import config
from utime import sleep_ms

class Battery():
    def __init__(self, state):
        self.state = state
        self.adc = ADC(config.BATT_ADC)
        self.timr = Timer(-1)
        state.battery, state.battery_level = self.read()

    def read(self):
        n = 10
        val = 0
        for i in range(n):
            sleep_ms(100)
            val += self.adc.read()
        percent = round(val / n / 1024 * 100)
        return (percent, round(percent / 20))

    def update(self):
        pc, lvl = self.read()
        self.state.set(
            battery = pc,
            battery_level = lvl,
        )

    def start(self):
        self._sched = False
        self.timr.deinit()
        
        def _cb(_):
            self._sched = False
            self.update()

        def cb(_):
            if not self._sched:
                self._sched = True
                schedule(_cb, None)
        
        self.timr.init(
            period=config.BATT_INT * 1000,
            callback=cb
        )

    def stop(self):
        self.timr.deinit()
