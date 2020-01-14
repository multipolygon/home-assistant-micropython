import config
from hub import Hub

hub = Hub(
    light = False,
    brightness = config.INIT_BRI,
    motion = False,
    enable = False,
    auto = False,
)

if config.BATT:
    from components.battery import Battery
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

if hasattr(config, 'RETAIN') and config.RETAIN:
    from components.retain import Retain
    hub.add(Retain, priority=True)

from components.daily_reset import DailyReset
hub.add(DailyReset)

hub.run()
