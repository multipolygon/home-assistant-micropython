from machine import Timer
from esp import deepsleep
from utime import sleep
import config
from machine import reset_cause, DEEPSLEEP_RESET

class Deepsleep():
    def __init__(self, hub):
        self.tmr = Timer(-1)

    def _active(self, hub):
        return hub.enable and hub.water

    def start(self, hub):
        self.tmr.deinit()
        
        def cb(_):
            t = config.ALARM_SLEEP if self._active(hub) else config.NORMAL_SLEEP
            print('deepsleep', t)
            hub.stop()
            sleep(5)
            deepsleep(t * 1000000)

        period = 60000 if self._active(hub) or reset_cause() != DEEPSLEEP_RESET else 10000

        self.tmr.init(
            period = period,
            mode = Timer.ONE_SHOT,
            callback = cb
        )

    def stop(self, hub):
        self.tmr.deinit()
