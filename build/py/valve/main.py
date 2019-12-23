import config
from lib.state import State

state = State(
    valve_open = False,
)

from ball_valve import BallValve
state.add(BallValve)

if config.BTN:
    from button import Button
    state.add(Button)

if config.BATT:
    from lib.components.battery import Battery
    state.add(Battery, priority = True)

from internet import Internet
internet = state.add(Internet)

try:
    internet.wait()
except KeyboardInterrupt:
    state.deinit()
