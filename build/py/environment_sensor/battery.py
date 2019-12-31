from analog import Analog
import config

class Battery(Analog):
    def __init__(self, state):
        state['battery'] = state['analog'] if config.BATT_ADC == config.ANALOG_ADC else self.percent(config.BATT_ADC)
