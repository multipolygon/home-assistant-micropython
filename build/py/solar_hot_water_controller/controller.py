from config import PUMP_ON, PUMP_OFF, pump_logic, pump_boost
from home_assistant.climate import MODE_OFF, MODE_AUTO, MODE_HEAT

class Controller():
    def __init__(self, state):
        self.update_on = ('mode', 'solar_temp', 'tank_temp', 'tank_target_temp')
        
    def update(self, state, changed):
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
