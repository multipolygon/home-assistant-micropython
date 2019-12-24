import config
from lib.state import State

state = State(
    valve_open = False,
)

from ball_valve import BallValve
valve = state.add(BallValve)

batt_low = False

if config.BATT:
    from lib.components.battery import Battery
    state.add(Battery)
    batt_low = valve.check_battery(state)

if not batt_low:
    if config.BTN:
        from button import Button
        state.add(Button)

    from internet import Internet
    internet = state.add(Internet)

    state.run()
