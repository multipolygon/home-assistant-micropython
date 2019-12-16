class StateAttributeError(AttributeError):
    pass

class State():
    def __init__(self, **kwargs):
        self.observers = []
        for key, val in kwargs.items():
            setattr(self, key, val)
                            
    def observer(self, cls):
        obj = cls(self)
        self.observers.append(obj)
        return obj

    def trigger(self, obj, fn, *args):
        if hasattr(obj, fn):
            print(" --> %s.%s()" % (obj.__class__.__name__, fn))
            getattr(obj, fn)(self, *args)

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
                self.trigger(obj, "on_state_change", changed)
                for key in changed:
                    self.trigger(obj, "on_%s_change" % key)
                    val = getattr(self, key)
                    if type(val) == type(True):
                        self.trigger(obj, "on_%s_%s" % (key, 'on' if val else 'off'))
