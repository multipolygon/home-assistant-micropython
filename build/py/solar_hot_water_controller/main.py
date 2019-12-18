from controller import Controller
from display import Display
from internet import Internet
from lib.state import State
from pump import Pump
from temperature import Temperature

state = State(
    solar_temperature = None,
    tank_temperature = None,
    tank_target_temperature = None,
    pump = False,
    mode = None,
    telemetry = False,
)


internet = state.observer(Internet)
state.observer(Display)
state.observer(Pump)
state.observer(Controller)
temperature = state.observer(Temperature)

try:
    temperature.poll()
    internet.wait_for_messages()
except KeyboardInterrupt:
    temperature.stop()
    print('Stop.')
