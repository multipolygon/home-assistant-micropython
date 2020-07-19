from gc import collect as gc_collect
from gc import mem_free, mem_alloc
from uos import statvfs
from time import sleep_ms

class Hub():
    def __init__(self, **kwargs):
        self.print(self.__class__, '__init__')
        s = statvfs('/')
        print('statvfs', round((s[2] - s[3]) / s[2] * 100), '%', 'of', round(s[1] * s[2] / pow(2,20), 1), 'mb')
        self.activ = False
        self.obj = []
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.mem_alloc()
                            
    def add(self, cls, priority=False):
        gc_collect()
        self.print(cls, '__init__')
        obj = cls(self)
        on = set(obj.update_on) if hasattr(obj, 'update') and hasattr(obj, 'update_on') else set()
        if on:
            print('update_on', ':', on)
        if priority:
            self.obj.insert(0, (obj, on))
        else:
            self.obj.append((obj, on))
        self.mem_alloc()
        return obj

    def run(self):
        self.print(self.__class__, 'run')
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
        self.print(self.__class__, 'start')
        for i in set((i for _, s in self.obj for i in s)):
            print(i, '=', getattr(self, i))
        self.activ = True
        for obj, _ in self.obj:
            if hasattr(obj, 'start'):
                self.print(obj.__class__, 'start')
                obj.start(self)
                self.mem_alloc()

    def stop(self):
        self.print(self.__class__, 'stop')
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
                if on & changed:
                    self.print(obj.__class__, 'update', pf='  ')
                    obj.update(self, changed)
                    sleep_ms(100)
                    self.mem_alloc()

    def print(self, cls, fn, pf=''):
        print('%s%s.%s' % (pf, cls.__name__, fn))

    def mem_alloc(self):
        gc_collect()
        print('    Mem: %d%%' % round(mem_alloc() / (mem_alloc() + mem_free()) * 100 ))
