from gc import collect as gc_collect
from rand import randint
from sys import print_exception
from uio import BytesIO
from ujson import dump as json_dump
from umqtt.simple import MQTTClient
from utime import sleep
from uos import stat
import machine
import wifi

UTF8 = 'utf-8'

class MQTT():
    def __init__(self, name, secrets, uid=None, led=None):
        self.name = name
        self.secrets = secrets
        self.uid = uid
        self.led = led
        self.state = {}
        self.obj = []
        self.cfg = []
        self.cb = {}
        self.do_pub_cfg = True
        self.reconnect = True
        self.mqtt = None
        self.topic = None
        self.mac = wifi.mac()
        self.err = 0

    def log(self, e):
        print('mqtt', self.err, ':')
        print_exception(e)
        n = 'mqtt' + '.' + 'log'
        m = 'a' if stat(n)[6] < 10000 else 'w' # reset log when it gets too big
        with open(n, m) as f:
            f.write("\n\n[%d]\n" % self.err)
            print_exception(e, f)

    def connect(self):
        self.discon()

        self.mqtt = MQTTClient(
            self.mac,
            self.secrets.MQTT_SERVER,
            keepalive=60,
            user=self.secrets.MQTT_USER.encode(UTF8),
            password=self.secrets.MQTT_PASSWORD.encode(UTF8)
        )

        def rx(tpc, msg):
            print('  >', 'rx', tpc)
            print('  >', 'rx', msg)
            try:
                msg = msg.decode(UTF8)
                gc_collect()
                for t, cb in self.cb.items():
                    if t == tpc:
                        print('  >', 'rx', 'cb')
                        cb(msg)
                        break
            except Exception as e:
                self.log(e)
            else:
                self.err = 0
        
        self.mqtt.set_callback(rx)

        self.mqtt.connect()
        sleep(0.5)
        
        if self.do_pub_cfg:
            self.do_pub_cfg = not(self.pub_cfg())
            sleep(0.5)
            
        if self.topic != None:
            print('subscribe', self.topic)
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

    def add(self, name, cls, prim = False, key = None, **cfg):
        obj = cls(
            prefix = self.secrets.MQTT_PREFIX,
            uid = self.uid,
            dev_name = self.name,
            name = name,
            prim = prim,
            key = key,
            state = self.state,
        )
        self.obj.append(obj)
        self.cfg.append(cfg)
        return obj

    def pub_cfg(self):
        if self.led:
            self.led.fast_blink()
        ok = True
        for i, obj in enumerate(self.obj):
            print(obj.__class__.__name__)
            gc_collect()
            if not self.pub_json(obj.cfg_tpc(), obj.cfg(**self.cfg[i]), retain=True):
                ok = False
                print('pub_cfg', 'err')
        if self.led:
            self.led.off()
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
                self.log(e)
                self.discon()
        self.do_pub_cfg = False
        return ok

    def set_attr(self, key, val):
        self.obj[0].set_attr(key, val)

    def set_wifi_attr(self):
        self.set_attr("ip", wifi.ip())
        self.set_attr("mac", self.mac)
        self.set_attr("rssi", wifi.rssi())

    def publish(self, tpc, msg, **kwarg):
        print('  <', 'tx', tpc)
        print('  <', 'tx', msg)
        if wifi.is_connected() and self.mqtt:
            if type(tpc) != type(b''):
                tpc = tpc.encode(UTF8)
            if type(msg) != type(b''):
                msg = msg.encode(UTF8)
            self.mqtt.publish(tpc, msg, **kwarg)
            sleep(0.5)
            print('  <', 'tx', 'ok')
            return True
        return False

    def pub_json(self, tpc, obj, **kwarg):
        gc_collect()
        with BytesIO() as json:
            json_dump(obj, json)
            gc_collect()
            ok = self.publish(tpc, json.getvalue(), **kwarg)
        gc_collect()
        return ok
    
    def pub_state(self):
        gc_collect()
        return self.pub_json(self.obj[0].base_tpc(), self.state)
        gc_collect()

    def sub(self, tpc, cb):
        print('sub', tpc)
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

    def sub_dev_cmd(self, tpc):
        def uid(msg):
            with open('uid' + '.py', 'w') as f:
                f.write('UID = "%s"' % msg)

        self.sub(tpc + '/' + 'uid', uid)

        def reset(msg):
            sleep(randint(3))
            machine.reset()

        self.sub(tpc + '/' + 'reset', reset)

        def secrets(msg):
            with open('secrets' + '.' + 'json', 'w') as f:
                f.write(msg)

        self.sub(tpc + '/' + 'secrets', secrets)

    def wait(self):
        while self.reconnect:
            try:
                self.connect()
                while True:
                    gc_collect()
                    self.mqtt.wait_msg()
            except Exception as e:
                self.err += 1
                self.log(e)
                self.discon()
                if self.err > 1000:
                    machine.reset()
                if self.err > 60:
                    if self.led:
                        led.slow_blink()
                    # add a bit of randomness in case every device on the network are all retrying at the same time:
                    sleep(60 + randint(3))
                    if self.led:
                        self.led.off()
                else:
                    sleep(self.err)
