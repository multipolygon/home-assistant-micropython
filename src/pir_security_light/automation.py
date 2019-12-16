from machine import Timer
from micropython import schedule
import config

STANDBY, ON_AUTO, ON_TIMER, ON_MANUAL, DISABLED = range(5)

edges = {
    STANDBY: {
        'automatic': { False: DISABLED },
        'light': { True: ON_MANUAL },
        'motion': { True: ON_AUTO },
    },
    ON_AUTO: {
        'automatic': { False: DISABLED },
        'light': { False: STANDBY },
        'motion': { False: ON_TIMER },
    },
    ON_TIMER: {
        'automatic': { False: DISABLED },
        'light': { False: STANDBY },
        'motion': { True: ON_AUTO },
    },
    ON_MANUAL: {
        'automatic': { False: DISABLED },
        'light': { False: STANDBY },
    },
    DISABLED: {
        'automatic': { True: STANDBY },
    },
}

class Automation():
    def __init__(self, state):
        self.mode = STANDBY
        timer = Timer(-1)

        def on_auto():
            print('ON_AUTO')
            timer.deinit()
            state.set(light = True)

        def _timeout(_):
            print('TIMEOUT')
            state.set(light = False)
            
        def _schedule_timeout(_):
            schedule(_timeout, None)

        def on_timer():
            print('ON_TIMER')
            timer.deinit()
            timer.init(
                period=config.MOTION_LIGHT_OFF_DELAY * 1000,
                mode=Timer.ONE_SHOT,
                callback=_schedule_timeout
            )

        def timer_deinit():
            print('CLEAR')
            timer.deinit()

        self.modes = {
            STANDBY: timer_deinit,
            ON_AUTO: on_auto,
            ON_TIMER: on_timer,
            ON_MANUAL: timer_deinit,
            DISABLED: timer_deinit,
        }

    def on_state_change(self, state, changed):
        for edge in changed:
            if edge in edges[self.mode]:
                val = getattr(state, edge)
                if val in edges[self.mode][edge]:
                    self.mode = edges[self.mode][edge][val]
                    self.modes[self.mode]()

