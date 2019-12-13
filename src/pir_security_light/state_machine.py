from machine import Timer
from micropython import schedule
import config

class State():
    def __init__(self, state):
        self.state = state
        self.__enter__()

    def __enter__(self):
        pass

    def __exit__(self):
        pass

    def __light(self, on):
        pass

    def set_brightness(self, percent):
        if self.state.brightness != percent:
            self.state.brightness = percent
            self.state.set_changed()

    def set_motion(self, detected):
        if self.state.motion != detected:
            self.state.motion = detected
            self.state.set_changed()
        
    def set_automatic(self, mode):
        if self.state.automatic != mode:
            self.state.automatic = mode
            self.state.set_changed()

class Off(State):
    def light(self, on):
        if on:
            self.state.goto('On')
            
    def motion(self, detected):
        if detected and self.state.automatic:
            self.state.goto('OnAuto')

class On(State):
    def light(self, on):
        if not on:
            self.state.goto('Off')

class OnAuto(State):
    def light(self, on):
        if on:
            self.state.goto('On')
        else:
            self.state.goto('Off')
        
    def motion(self, detected):
        if detected:
            self._clear_timer()
        else:
            self._set_timer()

    def auto_timeout(self):
        self.state.goto('Off')

    def __enter__(self):
        self.timer = Timer(-1)

    def __exit__(self):
        self._clear_timer()
    
    def _clear_timer(self):
        self.timer.deinit()

    def _set_timer(self):
        def timeout(*_):
            self.state.event('auto_timeout')
        def _timeout(*_):
            schedule(timeout, None)
        self.timer.init(
            period=config.MOTION_LIGHT_OFF_DELAY*1000,
            mode=Timer.ONE_SHOT,
            callback=_timeout
        )

class StateMachine():
    def __init__(self, on_change=None):
        self._state = Off(self)
        self._changed = False
        self._on_change = on_change
        
        self.brightness = config.INITIAL_BRIGHTNESS
        self.motion = False
        self.automatic = True

    def get_state(self):
        return self._state.__class__.__name__

    def goto(self, new_state):
        if self.get_state() != new_state:
            self._state.__exit__()
            self._state = globals()[new_state](self)
            self._changed = True

    def event(self, event, *args):
        self._changed = False
        
        if hasattr(self._state, 'set_' + event):
            getattr(self._state, 'set_' + event)(*args)

        if hasattr(self._state, event):
            getattr(self._state, event)(*args)

        if self._changed:
            if self._on_change:
                schedule(self._on_change, self)
                
        self._changed = False

    def set_changed(self):
        self._changed = True
