from uos import listdir
from ujson import load, dump
from config import RETAIN

FN = 'retain.json'

class Retain():
    def __init__(self, state):
        if FN in listdir():
            with open(FN) as f:
                obj = load(f)
                for k in obj:
                    if k not in RETAIN:
                        del k
                state.set(**obj)

    def on_state_change(self, state, changed):
        for k in changed:
            if k in RETAIN:
                obj = {}
                for k in RETAIN:
                    obj[k] = getattr(state, k)
                with open(FN, 'w') as f:
                    dump(obj, f)
                break
