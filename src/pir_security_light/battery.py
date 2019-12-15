from lib.esp8266.wemos.d1mini import pinmap
from machine import ADC

adc = ADC(pinmap.A0)
        
def percent():
    return round(adc.read() / 1024 * 100)
