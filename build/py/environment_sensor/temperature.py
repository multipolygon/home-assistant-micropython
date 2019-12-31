import esp8266.wemos.d1mini.pinmap as pinmap

class Temperature():
    def __init__(self, state):
        from vendor.sht30 import SHT30
        sht30 = SHT30(scl_pin = pinmap.SCL, sda_pin = pinmap.SDA)
        
        if sht30.is_present():
            t, rh = sht30.measure()
            state['temp'] = round(t,1)
            state['humid'] = round(rh)

        del sht30
