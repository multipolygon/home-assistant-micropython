from machine import unique_id
from ubinascii import hexlify
from utime import sleep
import network
import esp

from lib import secrets

esp.osdebug(None)

network.WLAN(network.AP_IF).active(False) ## Disable Access Point

sta_if = network.WLAN(network.STA_IF)

def is_connected():
    return sta_if.isconnected() and sta_if.status() == network.STAT_GOT_IP

def power_on():
    sta_if.active(True)
    
def power_off():
    ## Does this save power???
    sta_if.active(False)

def connect(timeout=30, power_save=False):
    print('WiFi Connecting...')
    power_on()
    sta_if.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
    for i in range(timeout):
        if is_connected():
            break
        else:
            print(i)
            sleep(1)
    if is_connected():
        print('WiFi connected.')
        return True
    else:
        print('WiFi timed out!')
        if power_save:
            power_off()
        return False

def disconnect(power_save=True):
    sta_if.disconnect()
    if power_save:
        power_off()

def rssi():
    return sta_if.status('rssi')

def uid():
    return hexlify(unique_id()).decode("utf-8").upper()

def mac():
    s = hexlify(network.WLAN().config('mac')).decode("utf-8").upper()
    return ":".join((s[i:i+2] for i in range(0,len(s),2)))

def signal_bars():
    if is_connected():
        n = rssi()
        if n < -90:
            return '.___'
        elif n < -60:
            return '..__'
        elif n < -30:
            return '..o_'
        elif n < 0:
            return '..oO'
        else:
            return 'E%d' % n
    else:
        return     '____'

def ip():
    if sta_if.status() == network.STAT_GOT_IP:
        return sta_if.ifconfig()[0]
    else:
        return ''
