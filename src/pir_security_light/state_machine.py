from machine import Timer
from micropython import schedule
import config
import gc

class OffAuto():
    def __init__(self, x):
        x.set_attr(
            light = False,
            motion = False,
        )
        
        self.edges = {
            'light_on': 'OnAuto',
            'automatic_off': 'OffManual',
            'motion_detected': 'OnAutoMotionDetected',
        }

class OnAuto():
    def __init__(self, x):
        x.set_attr(
            light = True,
            motion = False,
        )
        
        self.edges = {
            'light_off': 'OffAuto',
            'automatic_off': 'OnManual',
        }

class OnAutoMotionDetected():
    def __init__(self, x):
        self.x = x
        self._brightness = x.get_attr('brightness', config.INITIAL_BRIGHTNESS)
        
        x.set_attr(
            light = True,
            brightness = 80,
            motion =  True,
        )
        
        self.edges = {
            'light_on': 'OnAuto',
            'light_off': 'OffAuto',
            'automatic_off': 'OffManual',
            'motion_clear': 'OnAutoMotionClear',
        }

    def __deinit__(self):
        self.x.set_attr(brightness = self._brightness)

class OnAutoMotionClear():
    def __init__(self, x):
        x.set_attr(
            light = True,
            motion = False,
        )
        
        self.edges = {
            'light_on': 'OnAuto',
            'light_off': 'OffAuto',
            'automatic_off': 'OffManual',
            'motion_detected': 'OnAutoMotionDetected',
            'timeout': 'OffAuto',
        }
        
        def timeout(*_):
            x.trigger('timeout')
            
        def _timeout(*_):
            schedule(timeout, None)
            
        self.timer = Timer(-1)
        
        self.timer.init(
            period=config.MOTION_LIGHT_OFF_DELAY*1000,
            mode=Timer.ONE_SHOT,
            callback=_timeout
        )

    def __deinit__(self):
        self.timer.deinit()

class OffManual():
    def __init__(self, x):
        x.set_attr(
            light = False,
            motion = False,
        )
        
        self.edges = {
            'light_on': 'OnManual',
            'automatic_on': 'OffAuto',
            'motion_detected': 'OffManualMotionDetected',
        }
        
class OnManual():
    def __init__(self, x):
        x.set_attr(
            light = True,
            motion = False,
        )
        
        self.edges = {
            'light_off': 'OffManual',
            'automatic_on': 'OnAuto',
            'motion_detected': 'OnManualMotionDetected',
        }

class OffManualMotionDetected():
    def __init__(self, x):
        x.set_attr(
            light = False,
            motion = True,
        )
        
        self.edges = {
            'light_on': 'OnManualMotionDetected',
            'automatic_on': 'OnAutoMotionDetected',
            'motion_clear': 'OffManual',
        }

class OnManualMotionDetected():
    def __init__(self, x):
        x.set_attr(
            light = True,
            motion = True,
        )
        
        self.edges = {
            'light_off': 'OffManualMotionDetected',
            'automatic_on': 'OnAutoMotionDetected',
            'motion_clear': 'OnManual',
        }
        
class StateMachine():
    def __init__(self, on_change=None):
        self.attributes = {}
        self.on_change = None
        self.state = OffAuto(self)
        self.on_change = on_change

    def set_attr(self, **kwargs):
        changed = False
        for key, value in kwargs.items():
            if key not in self.attributes or self.attributes[key] != value:
                self.attributes[key] = value
                changed = True
        if changed and self.on_change:
            schedule(self.on_change, self)

    def get_attr(self, key, default=None):
        if key in self.attributes:
            return self.attributes[key]
        return default
            
    def trigger(self, edge, *args):
        if edge in self.state.edges:
            new_state = self.state.edges[edge]
            print('State: %s' % new_state)
            if hasattr(self.state, '__deinit__'):
                self.state.__deinit__()
            del self.state
            gc.collect()
            self.state = globals()[new_state](self)

    def get_state(self):
        return self.state.__class__.__name__
