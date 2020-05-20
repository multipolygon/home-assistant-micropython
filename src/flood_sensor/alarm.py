from machine import Pin
import config

class Alarm():
    def __init__(self, hub):
        self.update_on = ('enable', 'trigger')
        self.pin = Pin(config.ALARM_PIN, mode = Pin.OUT)
        self.pin.off()

    def _set_pin(self, hub):
        print('Alarm', ('On' if hub.enable and hub.trigger else 'Off'))
        self.pin.value(hub.enable and hub.trigger)
            
    def start(self, hub):
        self._set_pin(hub)

    def update(self, hub, changed):
        self._set_pin(hub)
            
    def stop(self, hub):
        self.pin.off()        
        
