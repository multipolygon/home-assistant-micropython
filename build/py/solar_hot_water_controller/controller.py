from config import pump_logic

STANDBY, ON_AUTO, ON_MANUAL, DISABLED = range(4)

class Controller():
    def __init__(self, state):
        self.state = state
        self.mode = STANDBY

    def on_state_change(self, state, changed):
        if 'solar_temperature' in changed or 'tank_temperature' in changed:
            if self.mode == STANDBY or self.mode == ON_AUTO:
                new_state = pump_logic(state)
                self.mode = ON_AUTO if new_state else STANDBY
                self.state.set(pump = new_state)

    def on_pump_on(self, state):
        if self.mode == STANDBY:
            self.mode = ON_MANUAL

    def on_pump_off(self, state):
        if self.mode != DISABLED:
            self.mode = STANDBY
                
    def on_automatic_on(self, state):
        if self.mode == DISABLED:
            self.mode = STANDBY

    def on_automatic_off(self, state):
        if self.mode == ON_AUTO:
            state.set(pump = False)
        self.mode = DISABLED
