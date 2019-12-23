from gc import collect as gc_collect
from gc import mem_free, mem_alloc

class State():
    def __init__(self, **kwargs):
        print()
        self._fn(self.__class__, '__init__')
        self.enabled = False
        self.obj = []
        for key, val in kwargs.items():
            setattr(self, key, val)
        self._mem()
                            
    def add(self, cls, priority=False):
        gc_collect()
        print()
        self._fn(cls, '__init__')
        obj = cls(self)
        if priority:
            self.obj.insert(0, obj)
        else:
            self.obj.append(obj)
        self._mem()
        return obj

    def start(self):
        self.enabled = True
        for obj in self.obj:
            if hasattr(obj, 'start'):
                print()
                self._fn(obj.__class__, 'start')
                obj.start()
                self._mem()

    def run(self):
        try:
            self.start()
            for obj in self.obj:
                if hasattr(obj, 'run'):
                    print()
                    self._fn(obj.__class__, 'run')
                    obj.run()
        except KeyboardInterrupt:
            self.stop()

    def trig(self, obj, fn, *args):
        if hasattr(obj, fn):
            self._fn(obj.__class__, fn, pf='  ')
            getattr(obj, fn)(self, *args)
            self._mem()

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
            
        if self.enabled and len(changed) != 0 and len(self.obj) != 0:
            for obj in self.obj:
                for key in changed:
                    self.trig(obj, 'on_%s_%s' % (key, 'on' if getattr(self, key) else 'off'))
                    self.trig(obj, 'on_%s_change' % key)
                self.trig(obj, 'on_state_change', changed)

    def stop(self):
        for obj in self.obj:
            if hasattr(obj, 'stop'):
                print()
                self._fn(obj.__class__, 'stop')
                obj.stop()
        del self.obj
        self._mem()

    def _fn(self, cls, fn, pf=''):
        print('%s%s.%s' % (pf, cls.__name__, fn))

    def _mem(self):
        gc_collect()
        print('    Mem: %d%%' % round(mem_alloc() / (mem_alloc() + mem_free()) * 100 ))
