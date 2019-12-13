from machine import unique_id
from ubinascii import hexlify
from utime import sleep
import network
import esp

class WiFi():
    def __init__(self, ssid, password):
        esp.osdebug(None)
        network.WLAN(network.AP_IF).active(False) ## Disable Access Point
        self.sta_if = network.WLAN(network.STA_IF)
        self.ssid = ssid
        self.password = password

    def is_connected(self):
        return self.sta_if.isconnected() and self.sta_if.status() == network.STAT_GOT_IP

    def power_on(self):
        self.sta_if.active(True)

    def power_off(self):
        ## Does this save power???
        self.sta_if.active(False)

    def connect(self, timeout=30, power_save=False):
        self.power_on()
        self.sta_if.connect(self.ssid, self.password)
        for i in range(timeout):
            if self.is_connected():
                break
            else:
                print(i)
                sleep(1)
        if self.is_connected():
            return True
        else:
            if power_save:
                power_off()
            return False

    def disconnect(self, power_save=True):
        self.sta_if.disconnect()
        if power_save:
            self.power_off()

    def rssi(self):
        return self.sta_if.status('rssi')

    def uid(self):
        return self.hexlify(unique_id()).decode("utf-8").upper()

    def mac(self):
        s = hexlify(network.WLAN().config('mac')).decode("utf-8").upper()
        return ":".join((s[i:i+2] for i in range(0,len(s),2)))

    def ip(self):
        if self.sta_if.status() == network.STAT_GOT_IP:
            return self.sta_if.ifconfig()[0]
        else:
            return ''
