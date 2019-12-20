from gc import collect as gc_collect
from lib.mem_info import mem_info

class StateAttributeError(AttributeError):
    pass

class State():
    def __init__(self, **kwargs):
        self.observers = []
        for key, val in kwargs.items():
            setattr(self, key, val)
        mem_info('State')
                            
    def observer(self, cls, priority=False):
        gc_collect()
        obj = cls(self)
        if priority:
            self.observers.insert(0, obj)
        else:
            self.observers.append(obj)
        mem_info(cls.__name__)
        return obj

    def trigger(self, obj, fn, *args):
        if hasattr(obj, fn):
            print(" --> %s.%s()" % (obj.__class__.__name__, fn))
            getattr(obj, fn)(self, *args)
            gc_collect()

    def set(self, **kwargs):
        changed = []
        
        for key, val in kwargs.items():
            if hasattr(self, key):
                if getattr(self, key) != val:
                    print('%s = %s' % (key, val))
                    setattr(self, key, val)
                    changed.append(key)
            else:
                raise StateAttributeError(key)
            
        if len(changed) != 0 and len(self.observers) != 0:
            for obj in self.observers:
                for key in changed:
                    self.trigger(obj, "on_%s_%s" % (key, 'on' if getattr(self, key) else 'off'))
                    self.trigger(obj, "on_%s_change" % key)
                self.trigger(obj, "on_state_change", changed)

    def deinit(self):
        for obj in self.observers:
            if hasattr(obj, 'deinit'):
                obj.deinit()
        del self.observers
        gc_collect()
