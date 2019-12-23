import config
from lib.state import State

state = State(
    auto = True,
    brightness = config.INIT_BRI,
    light = False,
    motion = False,
)

from internet import Internet
internet = state.add(Internet)

from light import Light
state.add(Light, priority=True)

if config.BTN:
    from button import Button
    state.add(Button)

if config.MOTN:
    from motion import Motion
    state.add(Motion)

    from auto import Auto
    state.add(Auto, priority=True)

if config.BATT:
    from battery import Battery
    state.add(Battery)

try:
    internet.wait()
except KeyboardInterrupt:
    state.deinit()
