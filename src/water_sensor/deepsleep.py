from machine import Timer
from esp import deepsleep
from utime import sleep
import config

class Deepsleep():
    def __init__(self, hub):
        self.tmr = Timer(-1)

    def start(self, hub):
        self.tmr.deinit()
        
        def cb(_):
            hub.stop()
            sleep(1)
            t = config.ALARM_SLEEP if hub.trigger else config.NORMAL_SLEEP
            print('sleep', t)
            deepsleep(t * 1000000)

        period = 60000 if hub.trigger else 5000

        self.tmr.init(
            period = period,
            mode = Timer.ONE_SHOT,
            callback = cb
        )

    def stop(self, hub):
        self.tmr.deinit()
