from lib.esp8266.wemos.d1mini import oled
import wifi
mqtt_connected = True ## TODO
config_sent = True
state_sent = True

class Display():
    def __init__(self, state):
        oled.write('POWER ON')

    def on_state_change(self, state, changed):
        oled.write('%-4s %s%s%s' % (
            wifi.rssi() if wifi.is_connected() else "LOS",
            "+" if mqtt_connected else "-",
            "+" if config_sent else "-",
            "+" if state_sent else "-"
        ), False)
        oled.write('SOL %4d' % state.solar_temperature, False)
        oled.write('TNK %4d' % state.tank_temperature, False)
        oled.write('PUMP %3s' % ('ON' if state.pump else 'OFF'))
