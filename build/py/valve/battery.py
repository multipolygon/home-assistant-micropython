from machine import ADC
from machine import Timer
from micropython import schedule
import config
from utime import sleep_ms

class Battery():
    def __init__(self, state):
        self.state = state
        self.adc = ADC(config.BATTERY_ADC)
        self.timer = Timer(-1)
        state.battery = self.percent()
        state.battery_level = self.level(state.battery)
        self.poll()

    def adc_read(self):
        val = 0
        for i in range(10):
            sleep_ms(100)
            val += self.adc.read()
        return val / 10

    def percent(self):
        return round(self.adc_read() / 1024 * 100)

    def level(self, percent):
        return round(percent / 20)

    def update(self):
        val = self.percent()
        self.state.set(
            battery = val,
            battery_level = self.level(val),
        )

    def on_valve_open_on(self, state):
        self.update()

    def poll(self):
        self.update_scheduled = False
        self.timer.deinit()
        
        def update(_):
            self.update_scheduled = False
            self.update()

        def schedule_update(_):
            if not self.update_scheduled:
                self.update_scheduled = True
                schedule(update, None)
        
        self.timer.init(period=config.BATTERY_UPDATE_INTERVAL * 1000, callback=schedule_update)

    def deinit(self):
        self.timer.deinit()
