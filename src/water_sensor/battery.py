import config
from machine import ADC
from utime import sleep_ms

class Battery():
    def __init__(self, hub):
        hub.battery = self.percent(config.BATT_ADC)

    def percent(self, pin):
        adc = ADC(pin)
        val = 0
        n = 20
        for i in range(n):
            sleep_ms(100)
            val += adc.read()
        return round(val / n / 1024 * 100)
