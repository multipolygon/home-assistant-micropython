from machine import Timer
from micropython import schedule
import config
import gc

class OffAuto():
    def __init__(self, x):
        self.edges = {
            'light_on': 'OnAuto',
            'automatic_off': 'OffManual',
            'motion_detected': 'OnAutoMotionDetected',
        }

class OnAuto():
    def __init__(self, x):
        self.edges = {
            'light_off': 'OffAuto',
            'automatic_off': 'OnManual',
        }

class OnAutoMotionDetected():
    def __init__(self, x):
        self.edges = {
            'light_on': 'OnAuto',
            'light_off': 'OffAuto',
            'automatic_off': 'OffManual',
            'motion_clear': 'OnAutoMotionClear',
        }

class OnAutoMotionClear():
    def __init__(self, x):
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

    def __del__(self):
        self.timer.deinit()

class OffManual():
    def __init__(self, x):
        self.edges = {
            'light_on': 'OnManual',
            'automatic_on': 'OffAuto',
            'motion_detected': 'OffManualMotionDetected',
        }
        
class OnManual():
    def __init__(self, x):
        self.edges = {
            'light_off': 'OffManual',
            'automatic_on': 'OnAuto',
            'motion_detected': 'OnManualMotionDetected',
        }

class OffManualMotionDetected():
    def __init__(self, x):
        self.edges = {
            'light_on': 'OnManualMotionDetected',
            'automatic_on': 'OnAutoMotionDetected',
            'motion_clear': 'OffManual',
        }

class OnManualMotionDetected():
    def __init__(self, x):
        self.edges = {
            'light_off': 'OffManualMotionDetected',
            'automatic_on': 'OnAutoMotionDetected',
            'motion_clear': 'OnManual',
        }
        
class StateMachine():
    def __init__(self, on_change=None):
        self.state = OffAuto(self)
        self.on_change = on_change

    def trigger(self, edge, *args):
        if edge in self.state.edges:
            new_state = self.state.edges[edge]
            print('State: %s' % new_state)
            del self.state
            gc.collect()
            self.state = globals()[new_state](self)
            if self.on_change:
                schedule(self.on_change, self)

    def get_state(self):
        return self.state.__class__.__name__
