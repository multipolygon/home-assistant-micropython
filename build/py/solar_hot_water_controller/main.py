import config
from lib.state import State

state = State(
    solar_temperature = None,
    tank_temperature = None,
    tank_target_temperature = config.TANK_TARGET_TEMPERATURE,
    pump = False,
    mode = 'auto',
    telemetry = False,
)

from internet import Internet
internet = state.observer(Internet)

from pump import Pump
state.observer(Pump, priority=True)

from controller import Controller
state.observer(Controller, priority=True)

from display import Display
state.observer(Display, priority=True)

from temperature import Temperature
state.observer(Temperature)

try:
    internet.wait_for_messages()
except KeyboardInterrupt:
    state.deinit()
