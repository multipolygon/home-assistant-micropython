import config
from hub import Hub

hub = Hub(
    valve_open = False,
)

from ball_valve import BallValve
valve = hub.add(BallValve)

batt_low = False

if config.BATT:
    from components.battery import Battery
    hub.add(Battery)
    batt_low = valve.check_battery(hub)

if not batt_low:
    if config.BTN:
        from button import Button
        hub.add(Button)

    from internet import Internet
    internet = hub.add(Internet)

    hub.run()
