import config
from lib.state import State

state = State(
    count = -1,
    battery = 100,
)

from internet import Internet
internet = state.add(Internet)

from counter import Counter
state.add(Counter)

if config.BATT:
    from lib.components.battery import Battery
    state.add(Battery)

try:
    internet.wait()
except KeyboardInterrupt:
    state.deinit()
