from lib.esp8266.wemos.d1mini import pinmap
from machine import ADC
import config
from machine import Timer
from micropython import schedule

class Battery():
    def __init__(self, state):
        adc = ADC(pinmap.A0)
        
        def update(x):
            print('Battery.update()')
            x = round(adc.read() / 1024 * 100)
            state.set(
                battery_percent = x,
                battery_level = round(x/20),
            )

        update(None)
        
        def timeout(x):
            print('Battery.timeout()')
            schedule(update, None)

        ## TODO: This line causes continuous `wdt reset` loop, no idea why.
        # Timer(-1).init(period=30000, callback=timeout)
