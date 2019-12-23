from config import PUMP_ON, PUMP_OFF, pump_logic, pump_boost
from lib.home_assistant.climate import MODE_OFF, MODE_AUTO, MODE_HEAT

class Controller():
    def update(self, state):
        if state.mode == MODE_OFF:
            state.set(pump = PUMP_OFF)

        elif state.mode == MODE_AUTO:
            pump = pump_logic(state)
            if pump != None:
                state.set(pump = pump)

        elif state.mode == MODE_HEAT:
            pump = pump_boost(state)
            state.set(
                pump = pump,
                mode = MODE_HEAT if pump == PUMP_ON else MODE_AUTO,
            )

        else:
            state.set(mode = MODE_AUTO)
    
    def on_state_change(self, state, changed):
        for i in ('mode', 'solar_temp', 'tank_temp', 'tank_target_temp'):
            if i in changed:
                self.update(state)
                break
