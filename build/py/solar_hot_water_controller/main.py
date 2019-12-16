from controller import Controller
from display import Display
from internet import Internet
from lib.state import State
from pump import Pump
from temperature import Temperature

state = State(
    solar_temperature = None,
    tank_temperature = None,
    pump = False,
    automatic = True,
    mode = None,
    telemetry = False,
)

state.observer(Pump)
state.observer(Controller)
state.observer(Display)

temperature = state.observer(Temperature)
internet = state.observer(Internet)

try:
    temperature.poll()
    internet.wait_for_messages()
except KeyboardInterrupt:
    temperature.stop()
