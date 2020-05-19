from gc import collect as gc_collect
from gc import mem_free, mem_alloc

class Hub():
    def __init__(self, **kwargs):
        self.print(self.__class__, '__init__')
        self.activ = False
        self.obj = []
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.mem_alloc()
                            
    def add(self, cls, priority=False):
        gc_collect()
        self.print(cls, '__init__')
        obj = cls(self)
        on = set(obj.update_on if hasattr(obj, 'update_on') else ())
        if priority:
            self.obj.insert(0, (obj, on))
        else:
            self.obj.append((obj, on))
        self.mem_alloc()
        return obj

    def run(self):
        try:
            self.start()
            for obj, _ in self.obj:
                if hasattr(obj, 'run'):
                    self.print(obj.__class__, 'run')
                    obj.run(self)
                    break
        except KeyboardInterrupt:
            self.stop()

    def start(self):
        self.activ = True
        for obj, _ in self.obj:
            if hasattr(obj, 'start'):
                self.print(obj.__class__, 'start')
                obj.start(self)
                self.mem_alloc()

    def stop(self):
        self.activ = False
        for obj, _ in self.obj:
            if hasattr(obj, 'stop'):
                self.print(obj.__class__, 'stop')
                obj.stop(self)
        self.mem_alloc()

    def get(self, k):
        if hasattr(self, k):
            return getattr(self, k)
        else:
            return None

    def set(self, **kwargs):
        changed = set()
        
        for k, v in kwargs.items():
            if hasattr(self, k):
                if getattr(self, k) != v:
                    print('%s = %s' % (k, v))
                    setattr(self, k, v)
                    changed.add(k)
            else:
                raise AttributeError(k)
            
        if self.activ and changed and self.obj:
            for obj, on in self.obj:
                if hasattr(obj, 'update'):
                    if on & changed:
                        self.print(obj.__class__, 'update', pf='  ')
                        obj.update(self, changed)
                        self.mem_alloc()

    def print(self, cls, fn, pf=''):
        print('%s%s.%s' % (pf, cls.__name__, fn))

    def mem_alloc(self):
        gc_collect()
        print('    Mem: %d%%' % round(mem_alloc() / (mem_alloc() + mem_free()) * 100 ))
