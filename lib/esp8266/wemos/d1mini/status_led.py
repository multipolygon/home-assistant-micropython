from machine import Pin

from lib.esp8266.wemos.d1mini import pinmap

led = Pin(pinmap.LED, Pin.OUT)

def on():
    led.off()

def off():
    led.on()

off()
