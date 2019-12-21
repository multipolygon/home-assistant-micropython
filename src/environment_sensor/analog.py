from machine import ADC
import config

class Analog():
    def __init__(self, state):
        self.adc = ADC(config.ANALOG_ADC)
        state.set(analog = self.percent())

    def percent(self):
        return round(self.adc.read() / 1024 * 100)
