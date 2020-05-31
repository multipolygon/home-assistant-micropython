from machine import Timer, reset
from rand import randint

N = 6

class DailyReset():
    def __init__(self, state):
        self.tmr = Timer(-1)
        self.hrs = (24 + randint(4)) * N

    def start(self, state):
        self.tmr.deinit()
        
        def cb(_):
            self.hrs -= 1
            if self.hrs == 0:
                reset()
        
        self.tmr.init(
            period = round(60 * 60 * 1000 / N),
            callback = cb
        )

    def stop(self, state):
        self.tmr.deinit()
