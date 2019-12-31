import esp8266.wemos.d1mini.pinmap as pinmap

class Illuminance():
    def __init__(self, state):
        from machine import Pin, I2C

        addr = 0x23
        
        i2c = I2C(
            scl = Pin(pinmap.SCL),
            sda = Pin(pinmap.SDA)
        )

        if addr in i2c.scan():
            from vendor.bh1750 import BH1750
            bh1750 = BH1750(i2c, addr)
            lux = bh1750.luminance(BH1750.ONCE_HIRES_1)
            bh1750.off()
            state['lux'] = round(lux)
            del bh1750
