from machine import ADC
import config

class Battery():
    def __init__(self, state):
        self.adc = ADC(config.BATTERY_ADC)
        state.set(battery = self.percent())

    def percent(self):
        return round(self.adc.read() / 1024 * 100)
