import esp
from utime import sleep
import pinmap
import status_led
import oled
import secrets
import wifi

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
