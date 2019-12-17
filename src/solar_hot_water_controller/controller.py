from config import PUMP_ON, PUMP_OFF, pump_logic, pump_boost

OFF='OFF'
WAIT='WAIT'
AUTO='AUTO'
BOOST='BOOST'

class Controller():
    def __init__(self, state):
        state.set(mode = WAIT)

    def on_pump_on(self, state):
        if state.mode == WAIT:
            state.set(mode = BOOST)

    def on_pump_off(self, state):
        if state.mode != OFF:
            state.set(mode = WAIT)
                
    def on_automatic_on(self, state):
        if state.mode == OFF:
            state.set(mode = WAIT)

    def on_automatic_off(self, state):
        if state.mode == AUTO:
            state.set(mode = OFF, pump = PUMP_OFF)
        else:
            state.set(mode = OFF)

    def on_state_change(self, state, changed):
        if 'solar_temperature' in changed or 'tank_temperature' in changed:
            if state.mode == OFF:
                state.set(pump = PUMP_OFF)

            elif state.mode == WAIT or state.mode == AUTO:
                new_state = pump_logic(state)
                if new_state != None:
                    state.set(
                        mode = AUTO if new_state == PUMP_ON else WAIT,
                        pump = new_state
                    )

            elif state.mode == BOOST:
                ## TODO: Timer off
                new_state = pump_boost(state)
                if new_state != None:
                    state.set(
                        mode = BOOST if new_state == PUMP_ON else WAIT,
                        pump = new_state
                    )
