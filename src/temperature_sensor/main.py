import config

state = {}

print('Temperature', '...')
from temperature import Temperature
Temperature(state)

print(state)

print('Internet', '...')
from internet import Internet
Internet(state)

print('Sleep for %s sec' % config.FREQ, '...')

## https://docs.micropython.org/en/latest/library/esp.html#esp.deepsleep
## Note, GPIO pin 16 (or D0 on the Wemos D1 Mini) must be wired to the Reset pin. See README
## Note: ESP8266 only - use machine.deepsleep() on ESP32
## https://docs.micropython.org/en/latest/esp8266/tutorial/powerctrl.html#deep-sleep-mode
from esp import deepsleep
deepsleep(config.FREQ * 1000000) 
