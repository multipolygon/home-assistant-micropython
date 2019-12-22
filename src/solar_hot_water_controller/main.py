from internet import Internet
from lib.state import State
import config

state = State(
    solar_temperature = None,
    tank_temperature = None,
    tank_target_temperature = config.TANK_TARGET_TEMPERATURE,
    pump = False,
    mode = 'auto',
    telemetry = False,
)

internet = state.observer(Internet)

from temperature import Temperature
state.observer(Temperature)

from display import Display
state.observer(Display, priority=True)

from controller import Controller
state.observer(Controller, priority=True)

from pump import Pump
state.observer(Pump, priority=True)

try:
    internet.wait_for_messages()
except KeyboardInterrupt:
    state.deinit()
