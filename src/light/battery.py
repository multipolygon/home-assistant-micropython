from machine import ADC
from machine import Timer
from micropython import schedule
import config

class Battery():
    def __init__(self, state):
        self.state = state
        self.adc = ADC(config.BATTERY_ADC)
        self.timer = Timer(-1)
        self.update()
        self.poll()

    def percent(self):
        return round(self.adc.read() / 1024 * 100)

    def update(self):
        self.state.set(battery = self.percent())

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
