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

from controller import Controller
state.observer(Controller)

from display import Display
state.observer(Display)

from pump import Pump
state.observer(Pump)

from temperature import Temperature
temperature = state.observer(Temperature)

try:
    temperature.poll()
    internet.wait_for_messages()
except KeyboardInterrupt:
    temperature.stop()
    print('Stop.')
