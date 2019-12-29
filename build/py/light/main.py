import config
from lib.hub import Hub

hub = Hub(
    light = False,
    brightness = config.INIT_BRI,
    motion = False,
    enable = False,
    auto = False,
)

if config.BATT:
    from lib.components.battery import Battery
    hub.add(Battery)

from internet import Internet
internet = hub.add(Internet)

from light import Light
hub.add(Light, priority=True)

if config.MOTN:
    from motion import Motion
    hub.add(Motion)

    from auto import Auto
    hub.add(Auto, priority=True)

if config.BTN:
    from button import Button
    hub.add(Button)

from lib.components.retain import Retain
hub.add(Retain, priority=True)

hub.run()
