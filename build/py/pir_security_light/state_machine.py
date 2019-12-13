from machine import Timer
from micropython import schedule
import config
import gc

class State():
    def set_brightness(self, percent):
        if self.state.brightness != percent:
            self.state.brightness = percent
            self.state._changed = True

class OffAuto(State):
    def light_on(self):
        self.state.goto('OnAuto')

    def automatic_off(self):
        self.state.goto('OffManual')
            
    def motion_detected(self):
        self.state.goto('OnAutoMotionDetected')

class OffManual(State):
    def light_on(self):
        self.state.goto('OnManual')

    def automatic_on(self):
        self.state.goto('OffAuto')

class OnAuto(State):
    def light_off(self):
        self.state.goto('OffAuto')

    def automatic_off(self):
        self.state.goto('OnManual')
        
class OnManual(State):
    def light_off(self):
        self.state.goto('OffManual')

    def automatic_on(self):
        self.state.goto('OnAuto')

class OnAutoMotionDetected(State):
    def light_on(self):
        self.state.goto('OnAuto')

    def light_off(self):
        self.state.goto('OffAuto')

    def automatic_off(self):
        self.state.goto('OffManual')

    def motion_clear(self):
        self.state.goto('OnAutoMotionClear')

class OnAutoMotionClear(State):
    def __enter__(self):
        def timeout(*_):
            self.state.event('auto_timeout')
        def _timeout(*_):
            schedule(timeout, None)
        self.timer = Timer(-1)
        self.timer.init(
            period=config.MOTION_LIGHT_OFF_DELAY*1000,
            mode=Timer.ONE_SHOT,
            callback=_timeout
        )

    def light_on(self):
        self.state.goto('OnAuto')

    def light_off(self):
        self.state.goto('OffAuto')

    def automatic_off(self):
        self.state.goto('OffManual')

    def motion_detected(self):
        self.state.goto('OnAutoMotionDetected')

    def auto_timeout(self):
        self.state.goto('OffAuto')

    def __exit__(self):
        self.timer.deinit()

class StateMachine():
    def __init__(self, initial_state, on_change=None):
        self._state = None
        self._changed = False
        self._on_change = on_change
        self.brightness = config.INITIAL_BRIGHTNESS
        self.goto(initial_state)

    def goto(self, new_state):
        if hasattr(self._state, '__exit__'):
            self._state.__exit__()
        self._state = globals()[new_state]()
        gc.collect()
        self._state.state = self
        if hasattr(self._state, '__enter__'):
            self._state.__enter__()
        self._changed = True

    def event(self, event, *args):
        self._changed = False
        if hasattr(self._state, event):
            getattr(self._state, event)(*args)
        if self._changed:
            if self._on_change:
                schedule(self._on_change, self)
        self._changed = False

    def get_state(self):
        return self._state.__class__.__name__
