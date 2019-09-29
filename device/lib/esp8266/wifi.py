import network
from utime import sleep

import secrets

network.WLAN(network.AP_IF).active(False) ## Disable Access Point

sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)

def isconnected():
    return sta_if.isconnected() and sta_if.status() == network.STAT_GOT_IP

def power_on():
    sta_if.active(True)
    
def power_off():
    ## Does this save power???
    sta_if.active(False)

def connect(timeout=30):
    print('WiFi Connecting...')
    power_on()
    sta_if.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
    for i in range(timeout):
        print(i)
        if isconnected():
            print('WiFi connected.')
            return True
        else:
            sleep(1)
    print('WiFi failed!')
    sta_if.active(False)
    return False

def rssi():
    return sta_if.status('rssi')

def sigbars():
    if isconnected():
        n = rssi()
        if n < -100:
            return 'o____'
        elif n < -80:
            return 'oo___'
        elif n < -60:
            return 'ooO__'
        elif n < -30:
            return 'ooOO_'
        elif n < 0:
            return 'ooOOO'
        else:
            return 'ERR: %d' % n
    else:
        return     '_____'

def ip():
    if sta_if.status() == network.STAT_GOT_IP:
        return sta_if.ifconfig()[0]
    else:
        return ''

power_off()
