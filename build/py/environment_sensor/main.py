from gc import collect as gc_collect
from gc import mem_free, mem_alloc
import config

print('Run...')

state = {}

def run(cls):
    print(cls.__name__)
    cls(state)
    gc_collect()
    print("Mem: %d%%" % round(mem_alloc() / (mem_alloc() + mem_free()) * 100 ))

if config.ANALOG_ENABLED:
    from analog import Analog
    run(Analog)

if config.BATTERY_ENABLED:
    from battery import Battery
    run(Battery)

from temperature import Temperature
run(Temperature)

from illuminance import Illuminance
run(Illuminance)

from internet import Internet
run(Internet)

print('Sleep: %s sec' % config.INTERVAL)

## https://docs.micropython.org/en/latest/library/esp.html#esp.deepsleep
## Note, GPIO pin 16 (or D0 on the Wemos D1 Mini) must be wired to the Reset pin. See README
## Note: ESP8266 only - use machine.deepsleep() on ESP32
## https://docs.micropython.org/en/latest/esp8266/tutorial/powerctrl.html#deep-sleep-mode
from esp import deepsleep
deepsleep(config.INTERVAL * 1000000) 
