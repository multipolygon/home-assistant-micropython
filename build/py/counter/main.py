from battery import Battery
from counter import Counter
from internet import Internet
from lib.state import State
import config

state = State(
    count = -1,
    battery = 100,
)

internet = state.observer(Internet)

state.observer(Counter)

if config.BATTERY_ENABLED:
    state.observer(Battery)

try:
    internet.wait_for_messages()
except KeyboardInterrupt:
    state.deinit()
