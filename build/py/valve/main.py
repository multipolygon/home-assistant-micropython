import config
from lib.state import State

state = State(
    valve_open = False,
)

from ball_valve import BallValve
state.observer(BallValve)

from button import Button
state.observer(Button)

if config.BATTERY_ENABLED:
    from battery import Battery
    state.observer(Battery, priority = True)

from internet import Internet
internet = state.observer(Internet)

try:
    internet.wait_for_messages()
except KeyboardInterrupt:
    state.deinit()
