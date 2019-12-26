from gc import collect as gc_collect
from lib.random import random_int
from sys import print_exception
from uio import BytesIO
from ujson import dump as json_dump
from umqtt.simple import MQTTClient
from utime import sleep
import wifi

UTF8 = 'utf-8'

class RxEx(Exception):
    pass

class MQTT():
    def __init__(self, name, secrets):
        self.name = name
        self.secrets = secrets
        self.state = {}
        self.obj = []
        self.cfg = []
        self.cb = {}
        self.do_pub_cfg = True
        self.reconnect = True
        self.mqtt = None
        self.topic = None
        self.mac = wifi.mac()

    def connect(self):
        self.discon()

        self.mqtt = MQTTClient(
            self.mac,
            self.secrets.MQTT_SERVER,
            user=self.secrets.MQTT_USER.encode(UTF8),
            password=self.secrets.MQTT_PASSWORD.encode(UTF8)
        )

        def rx(tpc, msg):
            msg = msg.decode(UTF8)
            gc_collect()
            try:
                for t, cb in self.cb.items():
                    if t == tpc:
                        cb(msg)
                        break
            except Exception as e:
                print_exception(e)
                raise RxEx()
        
        self.mqtt.set_callback(rx)

        self.mqtt.connect()
        sleep(0.5)
        
        if self.do_pub_cfg:
            self.do_pub_cfg = not(self.pub_cfg())
            sleep(0.5)
            
        if self.topic != None:
            self.mqtt.subscribe(self.topic)
            sleep(0.5)

        gc_collect()
            
    def discon(self):
        if self.mqtt != None:
            try:
                self.mqtt.disconnect()
            except:
                pass
            self.mqtt = None
        gc_collect()

    def add(self, name, cls, key = None, **cfg):
        obj = cls(
            scope = self.secrets.MQTT_USER,
            dev_name = self.name,
            name = name,
            key = key,
            state = self.state,
        )
        self.obj.append(obj)
        self.cfg.append(cfg)
        return obj

    def pub_cfg(self):
        ok = True
        for i, obj in enumerate(self.obj):
            print(obj.__class__.__name__)
            gc_collect()
            if not self.pub_json(obj.cfg_tpc(), obj.cfg(**self.cfg[i]), retain=True):
                ok = False
                print('>fail')
        return ok

    def try_pub_cfg(self):
        ok = False
        if wifi.is_connected():
            try:
                if not self.mqtt:
                    self.do_pub_cfg = True
                    self.connect()
                    ok = True
                else:
                    ok = self.pub_cfg()
            except Exception as e:
                print_exception(e)
                self.discon()
        self.do_pub_cfg = False
        return ok

    def set_attr(self, key, val):
        self.obj[0].set_attr(key, val)

    def set_wifi_attr(self):
        self.set_attr("ip", wifi.ip())
        self.set_attr("mac", self.mac)
        self.set_attr("rssi", wifi.rssi())

    def pub_json(self, tpc, obj, **kwarg):
        gc_collect()
        print(tpc)
        print(obj)
        if wifi.is_connected() and self.mqtt:
            if type(tpc) != type(b''):
                tpc = tpc.encode(UTF8)
            with BytesIO() as json:
                json_dump(obj, json)
                gc_collect()
                self.mqtt.publish(tpc, json.getvalue(), **kwarg)
                sleep(0.5)
            gc_collect()
            return True
        return False
    
    def pub_state(self):
        gc_collect()
        return self.pub_json(self.obj[0].base_tpc(), self.state)
        gc_collect()

    def sub(self, tpc, cb):
        gc_collect()
        self.cb[tpc.encode(UTF8)] = cb
        first = next(iter(self.cb))
        if len(self.cb) == 1:
            self.topic = first
        else:
            self.topic = b''
            for i, char in enumerate(first):
                for t in self.cb.keys():
                    if t[i] != char:
                        char = None
                        break
                if char == None:
                    break
                else:
                    self.topic += chr(char)
            self.topic += b'#'
        gc_collect()

    def wait(self, led=None):
        while self.reconnect:
            try:
                if wifi.is_connected():
                    self.connect()
                    while True:
                        gc_collect()
                        try:
                            self.mqtt.wait_msg()
                        except RxEx:
                            pass
                else:
                    print('No WiFi')
            except Exception as e:
                print('MQTT' + ':')
                print_exception(e)
                self.discon()
            if self.reconnect:
                if led:
                    led.slow_blink()
                    sleep(random_int(5))
                    led.off()
                else:
                    sleep(random_int(8))
