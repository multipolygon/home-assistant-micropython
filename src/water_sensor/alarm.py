from machine import Pin
import config

class Alarm():
    def __init__(self, hub):
        self.update_on = ['enable', 'water']
        self.pin = Pin(config.ALARM_PIN, mode = Pin.OUT)
        self.pin.off()
        hub.alarm = False

    def _set_pin(self, hub):
        self.pin.value(hub.enable and hub.water)
        hub.set(alarm=hub.enable and hub.water)
            
    def start(self, hub):
        self._set_pin(hub)

    def update(self, hub, changed):
        self._set_pin(hub)
            
    def stop(self, hub):
        self.pin.off()        
        
