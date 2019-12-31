from esp8266.wemos.d1mini.oled import OLED
from utime import sleep
import wifi

class Display():
    def __init__(self, state):
        self.update_on = ('mqtt', 'solar_temp', 'tank_temp', 'tank_target_temp', 'mode', 'pump')
        self.oled = OLED()
        self.mqtt(state)
        
    def mqtt(self, state):
        self.oled.write_lines(
            'WIFI:',
            ('%8d' % wifi.rssi()) if wifi.is_connected() else ('%8s' % '--'),
            'MQTT:',
            '%8s' % ('OK' if state.mqtt else '--'),
        )            
    
    def update(self, state, changed):
        if 'mqtt' in changed:
            self.mqtt(state)
        else:
            self.oled.write_lines(
                'SOLR:%3d' % state.solar_temp,
                'TANK:%3d' % state.tank_temp,
                'TARG:%3d' % state.tank_target_temp,
                '%-5s%3s' % (state.mode.upper(), 'ON' if state.pump else 'OFF'),
            )

    def stop(self, state):
        self.oled.clear()
        self.oled.power_off()
