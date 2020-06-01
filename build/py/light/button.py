from machine import Pin, Timer
from micropython import schedule
from config import BTN_GPIO

class Button():
    def __init__(self, hub):
        self.btn = Pin(BTN_GPIO, mode=Pin.IN)
        self.tmr = Timer(-1)

        def _tmr_cb(_):
            self._en = 1
            self.btn.irq(
                handler=self._btn_cb,
                trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
            )
            
        def _sched_cb(_):
            self.tmr.init(
                period = 3000,
                mode = Timer.ONE_SHOT,
                callback = _tmr_cb
            )            
            hub.set(light = not(hub.light), light_cmd = True)

        def _btn_cb(_):
            self.btn.irq(trigger=0)
            if self._en:
                self._en = 0
                schedule(_sched_cb, None)

        self._tmr_cb = _tmr_cb
        self._btn_cb = _btn_cb
        
    def start(self, hub):
        self._tmr_cb(None)

    def stop(self, hub):
        self.pin.irq(trigger=0)
        self.tmr.deinit()
        
