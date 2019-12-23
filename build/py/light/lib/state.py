from gc import collect as gc_collect
from gc import mem_free, mem_alloc

class State():
    def __init__(self, **kwargs):
        self.obj = []
        for key, val in kwargs.items():
            setattr(self, key, val)
        self.mem_info('State')
                            
    def add(self, cls, priority=False):
        gc_collect()
        obj = cls(self)
        if priority:
            self.obj.insert(0, obj)
        else:
            self.obj.append(obj)
        self.mem_info(cls.__name__)
        return obj

    def trig(self, obj, fn, *args):
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
                raise AttributeError(key)
            
        if len(changed) != 0 and len(self.obj) != 0:
            for obj in self.obj:
                for key in changed:
                    self.trig(obj, "on_%s_%s" % (key, 'on' if getattr(self, key) else 'off'))
                    self.trig(obj, "on_%s_change" % key)
                self.trig(obj, "on_state_change", changed)

    def deinit(self):
        for obj in self.obj:
            if hasattr(obj, 'deinit'):
                obj.deinit()
        del self.obj
        gc_collect()

    def mem_info(self, s=''):
        gc_collect()
        print("Mem: %d%% [%s]" % (round(mem_alloc() / (mem_alloc() + mem_free()) * 100 ), s))
