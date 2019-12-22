from lib.esp8266.wemos.d1mini import pinmap

class Temperature():
    def __init__(self, state):
        from lib.esp8266.sht30.sht30 import SHT30
        sht30 = SHT30(scl_pin = pinmap.SCL, sda_pin = pinmap.SDA)
        
        if sht30.is_present():
            t, rh = sht30.measure()
            state['temperature'] = t
            state['humidity'] = rh

        del sht30
