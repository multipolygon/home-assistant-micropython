from machine import Timer
from micropython import schedule
import config

STANDBY, AUTO, MANUAL = range(3)

class Automation():
    def __init__(self, state):
        self.mode = STANDBY
        self.timer = Timer(-1)

        def timeout(_):
            state.set(light = False)
            
        def schedule_timeout(_):
            schedule(timeout, None)

        self.timeout = schedule_timeout

    def on_light_on(self, state):
        if self.mode == STANDBY:
            self.mode = MANUAL

    def on_light_off(self, state):
        self.timer.deinit()
        self.mode = STANDBY

    def on_motion_on(self, state):
        self.timer.deinit()
        if state.automatic_mode and MANUAL != self.mode:
            self.mode = AUTO
            state.set(light = True)
            
    def on_motion_off(self, state):
        self.timer.deinit()
        if AUTO == self.mode:
            self.timer.init(
                period=config.MOTION_LIGHT_OFF_DELAY * 1000,
                mode=Timer.ONE_SHOT,
                callback=self.timeout
            )
