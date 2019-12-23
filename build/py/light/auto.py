from machine import Timer
from micropython import schedule
import config

WAIT, ON_AUTO, ON_MAN, OFF = range(4)

class Auto():
    def __init__(self, state):
        self.mode = WAIT
        self.timr = Timer(-1)

        def off(_):
            state.set(light = False)
            
        def sched_off(_):
            schedule(off, None)

        self.off = sched_off

    def on_auto_on(self, state):
        if self.mode == OFF:
            self.mode = WAIT

    def on_auto_off(self, state):
        if self.mode == ON_AUTO:
            self.timr.deinit()
            state.set(light = False)
        self.mode = OFF

    def on_light_on(self, state):
        if self.mode == WAIT:
            self.mode = ON_MAN

    def on_light_off(self, state):
        self.timr.deinit()
        if self.mode != OFF:
            self.mode = WAIT

    def on_motion_on(self, state):
        self.timr.deinit()
        if self.mode == WAIT:
            self.mode = ON_AUTO
            state.set(light = True)
            
    def on_motion_off(self, state):
        self.timr.deinit()
        if self.mode == ON_AUTO:
            self.timr.init(
                period=config.MOTN_TIME * 1000,
                mode=Timer.ONE_SHOT,
                callback=self.off
            )

    def deinit(self):
        self.timr.deinit()
