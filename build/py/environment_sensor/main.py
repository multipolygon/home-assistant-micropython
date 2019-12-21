from lib.state import State
import config

state = State(
    analog = None,
    battery = None,
    humidity = None,
    illuminance = None,
    temperature = None,
)

if config.ANALOG_ENABLED:
    from analog import Analog
    state.observer(Analog)

if config.BATTERY_ENABLED:
    from battery import Battery
    state.observer(Battery)

from temperature import Temperature
state.observer(Temperature)

from illuminance import Illuminance
state.observer(Illuminance)

from internet import Internet
state.observer(Internet)
from internet import Internet

from utime import sleep
sleep(10)

state.deinit()
    
print('Sleep for %s sec.' % config.INTERVAL)

## https://docs.micropython.org/en/latest/library/esp.html#esp.deepsleep
## Note, GPIO pin 16 (or D0 on the Wemos D1 Mini) must be wired to the Reset pin. See README
## Note: ESP8266 only - use machine.deepsleep() on ESP32
## https://docs.micropython.org/en/latest/esp8266/tutorial/powerctrl.html#deep-sleep-mode
from esp import deepsleep
deepsleep(config.INTERVAL * 1000000) 
