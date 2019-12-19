from config import PUMP_ON, PUMP_OFF, pump_logic, pump_boost
from lib.home_assistant.climate import MODE_OFF, MODE_AUTO, MODE_HEAT

OBSERVE = (
    'mode',
    'solar_temperature',
    'tank_temperature',
    'tank_target_temperature',
)

class Controller():
    def on_state_change(self, state, changed):
        for i in OBSERVE:
            if i in changed:
                if state.mode == MODE_OFF:
                    state.set(pump = PUMP_OFF)

                elif state.mode == MODE_AUTO:
                    new_state = pump_logic(state)
                    if new_state != None:
                        state.set(pump = new_state)

                elif state.mode == MODE_HEAT:
                    new_state = pump_boost(state)
                    state.set(
                        pump = new_state,
                        mode = MODE_HEAT if new_state == PUMP_ON else MODE_AUTO,
                    )
                        
                break
