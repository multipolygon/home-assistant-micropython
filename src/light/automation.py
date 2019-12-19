from machine import Timer
from micropython import schedule
import config

STANDBY, ON_AUTO, ON_MANUAL, DISABLED = range(4)

class Automation():
    def __init__(self, state):
        self.mode = STANDBY
        self.timer = Timer(-1)

        def timeout(_):
            state.set(light = False)
            
        def schedule_timeout(_):
            schedule(timeout, None)

        self.timeout = schedule_timeout

    def on_automatic_on(self, state):
        if self.mode == DISABLED:
            self.mode = STANDBY

    def on_automatic_off(self, state):
        if self.mode == ON_AUTO:
            self.timer.deinit()
            state.set(light = False)
        self.mode = DISABLED

    def on_light_on(self, state):
        if self.mode == STANDBY:
            self.mode = ON_MANUAL

    def on_light_off(self, state):
        self.timer.deinit()
        if self.mode != DISABLED:
            self.mode = STANDBY

    def on_motion_on(self, state):
        self.timer.deinit()
        if self.mode == STANDBY:
            self.mode = ON_AUTO
            state.set(light = True)
            
    def on_motion_off(self, state):
        self.timer.deinit()
        if self.mode == ON_AUTO:
            self.timer.init(
                period=config.MOTION_LIGHT_OFF_DELAY * 1000,
                mode=Timer.ONE_SHOT,
                callback=self.timeout
            )
