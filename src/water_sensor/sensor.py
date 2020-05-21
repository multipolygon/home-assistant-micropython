from machine import Pin
import config
from utime import sleep_ms

class Sensor():
    def __init__(self, hub):
        out_pin = Pin(config.OUT_PIN, mode = Pin.OUT)
        in_pin = Pin(config.IN_PIN, mode = Pin.IN)
        out_pin.on()
        sleep_ms(100)
        hub.water = in_pin.value() == 1
        out_pin.off()
        
