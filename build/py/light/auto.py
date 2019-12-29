from machine import Timer
from micropython import schedule
from config import MOTN_TIME

OFF, ON, AUTO = 0, 1, 2

class Auto():
    def __init__(self, state):
        self.update_on = ('motion', 'light', 'auto')
        self.mode = OFF
        self.tmr = Timer(-1)

        def _cb(_):
            state.set(light = False)
            
        def cb(_):
            schedule(_cb, None)

        self.cb = cb

    def update(self, state, changed):
        if 'motion' in changed:
            self.tmr.deinit()
            if state.motion:
                if state.auto and self.mode == OFF:
                    self.mode = AUTO
                    state.set(light = True)
            else:
                if self.mode == AUTO:
                    self.tmr.init(
                        period = MOTN_TIME * 1000,
                        mode = Timer.ONE_SHOT,
                        callback = self.cb
                    )

        if 'light' in changed:
            if state.light:
                if self.mode == OFF:
                    self.mode = ON
            else:
                self.mode = OFF

        if 'auto' in changed:
            if self.mode == AUTO and not state.auto:
                self.tmr.deinit()
                state.set(light = False)

    def stop(self, state):
        self.tmr.deinit()
