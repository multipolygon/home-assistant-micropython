from machine import ADC
from machine import Timer
from micropython import schedule
from config import BATT_ADC, BATT_INT
from utime import sleep_ms

class Battery():
    def __init__(self, state):
        self.adc = ADC(BATT_ADC)
        self.tmr = Timer(-1)
        state.battery, state.battery_level = self.read()

    def read(self):
        n = 10
        v = 0
        for i in range(n):
            sleep_ms(100)
            v += self.adc.read()
        pc = round(v / n / 1024 * 100)
        return (pc, round(pc / 20))

    def start(self, state):
        self._sched = False
        self.tmr.deinit()
        
        def _cb(_):
            self._sched = False
            pc, n = self.read()
            state.set(
                battery = pc,
                battery_level = n,
            )

        def cb(_):
            if not self._sched:
                self._sched = True
                schedule(_cb, None)
        
        self.tmr.init(
            period = BATT_INT * 1000,
            callback = cb
        )

    def stop(self, state):
        self.tmr.deinit()
