from uos import listdir
from ujson import load, dump
from config import RETAIN

class Retain():
    F = 'retain.json'
    
    def __init__(self, state):
        self.update_on = RETAIN
        if self.F in listdir():
            with open(self.F) as f:
                try:
                    d = load(f)
                except:
                    d = {}
            state.set(**{k: d[k] for k in RETAIN if k in d})

    def update(self, state, changed):
        with open(self.F, 'w') as f:
            dump({k: getattr(state, k) for k in RETAIN}, f)
