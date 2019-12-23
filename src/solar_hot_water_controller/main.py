import config
from lib.state import State

state = State(
    solar_temp = None,
    tank_temp = None,
    tank_target_temp = config.TANK_TARGET_TEMP,
    pump = False,
    mode = 'auto',
)

from internet import Internet
internet = state.add(Internet)

from temperature import Temperature
state.add(Temperature)

from display import Display
state.add(Display, priority=True)

from controller import Controller
state.add(Controller, priority=True)

from pump import Pump
state.add(Pump, priority=True)

try:
    internet.wait()
except KeyboardInterrupt:
    state.deinit()
