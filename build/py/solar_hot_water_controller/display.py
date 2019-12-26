from lib.esp8266.wemos.d1mini.oled import OLED
from utime import sleep
import wifi

class Display():
    def __init__(self, status):
        self.oled = OLED()
        self.show_wifi(status)
        
    def show_wifi(self, status):
        self.oled.write_lines(
            'WIFI:',
            ('%8d' % wifi.rssi()) if wifi.is_connected() else ('%8s' % '--'),
            'MQTT:',
            '%8s' % ('OK' if status.mqtt else '--'),
        )            
    
    def on_state_change(self, state, changed):
        if 'mqtt' in changed:
            self.show_wifi(state)
        else:
            self.oled.write_lines(
                'SOLR:%3d' % state.solar_temp,
                'TANK:%3d' % state.tank_temp,
                'TARG:%3d' % state.tank_target_temp,
                '%-5s%3s' % (state.mode.upper(), 'ON' if state.pump else 'OFF'),
            )

    def stop(self):
        self.oled.clear()
        self.oled.power_off()
