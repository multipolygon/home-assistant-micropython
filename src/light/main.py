import config
from hub import Hub

hub = Hub(
    light = False,
    light_cmd = False,
    brightness = config.INIT_BRI,
    motion = False,
    enable = False,
    auto = False,
    battery = 100,
)

config.RETAIN = set(('light',))

if config.BRIGHTNESS:
    config.RETAIN.add('brightness')

if config.BATT:
    config.RETAIN.add('battery')

if config.MOTN:
    config.RETAIN.add('auto')

if len(config.RETAIN) > 0:
    from components.retain import Retain
    hub.add(Retain)

from light import Light
hub.add(Light, priority=True) # put light above retain

## internet has to go 2nd because it needs to allocate a lot of memory:
from internet import Internet
internet = hub.add(Internet)

if config.BATT:
    from components.battery import Battery
    hub.add(Battery)

if config.MOTN:
    from motion import Motion
    hub.add(Motion)

    from auto import Auto
    hub.add(Auto, priority=True) # put auto above light

if config.BTN:
    from button import Button
    hub.add(Button)

hub.run()
