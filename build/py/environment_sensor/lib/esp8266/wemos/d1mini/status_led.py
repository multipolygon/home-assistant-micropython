from machine import Pin, PWM

from lib.esp8266.wemos.d1mini import pinmap

led = Pin(pinmap.LED, Pin.OUT)
pwm = PWM(led)

def on():
    pwm.deinit()
    led.off()

def off():
    pwm.deinit()
    led.on()

def invert():
    pwm.deinit()
    led.value(not led.value())

def set(state):
    if state:
        on()
    else:
        off()

def slow_blink():
    pwm.freq(1)
    pwm.duty(512)
    
def fast_blink():
    pwm.freq(3)
    pwm.duty(512)

off()
