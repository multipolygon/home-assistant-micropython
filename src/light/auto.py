from machine import Timer
from micropython import schedule
from config import MOTN_TIME

OFF, ON, AUTO = 0, 1, 2

class Auto():
    def __init__(self, hub):
        self.update_on = ('motion', 'light', 'auto')
        self.mode = OFF
        self.tmr = Timer(-1)

        def _cb(_):
            hub.set(light = False)
            
        def cb(_):
            schedule(_cb, None)

        self.cb = cb

    def update(self, hub, changed):
        if 'motion' in changed:
            self.tmr.deinit()
            if hub.motion:
                if hub.auto and self.mode == OFF:
                    self.mode = AUTO
                    hub.set(light = True)
            else:
                if self.mode == AUTO:
                    self.tmr.init(
                        period = MOTN_TIME * 1000,
                        mode = Timer.ONE_SHOT,
                        callback = self.cb
                    )

        if 'light' in changed:
            if hub.light:
                if self.mode == OFF:
                    self.mode = ON
            else:
                self.mode = OFF

        if 'auto' in changed:
            if self.mode == AUTO and not hub.auto:
                self.tmr.deinit()
                hub.set(light = False)

    def stop(self, hub):
        self.tmr.deinit()
