from machine import Pin

import pinmap

led = Pin(pinmap.LED, Pin.OUT)

def on():
    led.off()

def off():
    led.on()

off()
