from analog import Analog
import config

class Battery(Analog):
    def __init__(self, state):
        state['battery'] = self.percent(config.BATT_ADC)
