from micropython import schedule

class StateAttributeError(AttributeError):
    pass

class State():
    def __init__(self, **kwargs):
        self.callbacks = []
        for key, val in kwargs.items():
            setattr(self, key, val)

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
        if len(changed) != 0 and len(self.callbacks) != 0:
            for cb, on in self.callbacks:
                for key in changed:
                    if key in on:
                        schedule(cb, self)
                        break
                
    def set_callback(self, cb, on=[]):
        self.callbacks.append((cb, on))
