from uos import listdir
from ujson import load, dump
from config import RETAIN

class Retain():
    F = 'retain.json'
    
    def __init__(self, hub):
        self.update_on = RETAIN
        if self.F in listdir():
            with open(self.F) as f:
                try:
                    d = load(f)
                except:
                    d = {}
            for k in RETAIN:
                if k in d:
                    setattr(hub, k, d[k])

    def update(self, state, changed):
        pass
