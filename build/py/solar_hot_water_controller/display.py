from lib.esp8266.wemos.d1mini import oled
from utime import sleep
import wifi

class Display():
    def __init__(self, status):
        self.show_telemetry(status)
        
    def show_telemetry(self, status):
        oled.write('WiFi:', False)
        oled.write(('%8d' % wifi.rssi()) if wifi.is_connected() else "      No", False)
        oled.write('MQTT:', False)
        oled.write('%8s' % ('Ok' if status.telemetry else 'No'))
        sleep(2)
    
    def on_state_change(self, state, changed):
        if 'telemetry' in changed:
            self.show_telemetry(state)
        else:
            oled.write('SOLR:%3d' % state.solar_temperature, False)
            oled.write('TANK:%3d' % state.tank_temperature, False)
            oled.write('TRGT:%3d' % state.tank_target_temperature, False)
            oled.write('%-5s%3s' % (state.mode.upper() + ':', 'ON' if state.pump else 'OFF'))
