import esp
from utime import sleep

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.wemos.d1mini import oled
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led

status_led.on()
oled.write('POWER ON')

wifi.connect(1)

bling = "/\\"

for i in range(5 * 60):
    status_led.on()
    oled.write('%1s%7d' % (bling[i % 2], wifi.rssi()))
    sleep(0.5)
    status_led.off()
    sleep(0.5)

oled.power_off()
wifi.power_off()
esp.deepsleep()
