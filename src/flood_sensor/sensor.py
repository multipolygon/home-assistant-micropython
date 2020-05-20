from machine import Pin
import config
from utime import sleep_ms

class Sensor():
    def __init__(self, hub):
        pin = Pin(config.SENSOR_PIN, mode = Pin.IN)
        hub.trigger = pin.value()
