## Just a bunch of wrappers with human-readable names ##
from utime import sleep
import network
from esp import osdebug

osdebug(None)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)

def no_ap():
    network.WLAN(network.AP_IF).active(False)

def is_connected():
    return sta_if.isconnected() and sta_if.status() == network.STAT_GOT_IP

def activate():
    sta_if.active(True)

def deactivate():
    ## Does this actually save power???
    sta_if.active(False)

def connect(ssid, password, timeout=30, power_save=False, led=None):
    if led:
        led.slow_blink()
    no_ap()
    activate()
    sta_if.connect(ssid, password)
    for i in range(timeout):
        if is_connected():
            break
        else:
            print('WiFi:%d' % i)
            sleep(1)
    print('wifi', 'ok' if is_connected() else 'err')
    if not(is_connected()) and power_save:
        deactivate()
    if led:
        led.off()
    return is_connected()

def disconnect(power_save=True):
    if is_connected():
        sta_if.disconnect()
    if power_save:
        deactivate()

def rssi():
    return sta_if.status('rssi')

def uid():
    from machine import unique_id
    from ubinascii import hexlify
    return hexlify(unique_id()).decode("utf-8").upper()

def mac():
    from ubinascii import hexlify
    s = hexlify(network.WLAN().config('mac')).decode("utf-8").upper()
    return "".join((s[i:i+2] for i in range(0,len(s),2)))

def ip():
    if sta_if.status() == network.STAT_GOT_IP:
        return sta_if.ifconfig()[0]
    else:
        return ''
