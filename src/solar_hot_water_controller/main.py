from controller import Controller
from display import Display
from internet import Internet
from lib.state import State
from pump import Pump
from temperature import Temperature
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

state.observer(Pump, priority=True)

state.observer(Controller, priority=True)

state.observer(Display, priority=True)

state.observer(Temperature)

try:
    internet.wait_for_messages()
except KeyboardInterrupt:
    state.deinit()
