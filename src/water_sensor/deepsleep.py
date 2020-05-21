from machine import Timer
from esp import deepsleep
from utime import sleep
import config

class Deepsleep():
    def __init__(self, hub):
        self.update_on = ['internet']
        self.tmr = Timer(-1)

    def _set_tmr(self, hub):
        self.tmr.deinit()
        
        def cb(_):
            t = config.ALARM_SLEEP if hub.water and hub.enable else config.NORMAL_SLEEP
            print('deepsleep', t)
            try:
                hub.stop()
            except:
                pass
            sleep(5)
            deepsleep(t * 1000000)

        self.tmr.init(
            period = (60000 if hub.internet else 10000),
            mode = Timer.ONE_SHOT,
            callback = cb
        )

    def start(self, hub):
        self._set_tmr(hub)

    def update(self, hub, changed):
        self._set_tmr(hub)

    def stop(self, hub):
        self.tmr.deinit()
