import config
from lib.state import State

state = State(
    count = -1,
    battery = 100,
)

from internet import Internet
internet = state.observer(Internet)

from counter import Counter
state.observer(Counter)

if config.BATTERY_ENABLED:
    from battery import Battery
    state.observer(Battery)

try:
    internet.wait_for_messages()
except KeyboardInterrupt:
    state.deinit()
