from uos import listdir
from ujson import load, dump
from config import RETAIN

FN = 'retain.json'

class Retain():
    def __init__(self, state):
        if FN in listdir():
            with open(FN) as f:
                obj = load(f)
            state.set(**{k: obj[k] for k in RETAIN if k in obj})

    def on_state_change(self, state, changed):
        for k in changed:
            if k in RETAIN:
                with open(FN, 'w') as f:
                    dump({k: getattr(state, k) for k in RETAIN}, f)
                break
