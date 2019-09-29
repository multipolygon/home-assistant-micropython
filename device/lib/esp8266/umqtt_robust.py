## https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/umqtt/simple.py
## https://github.com/micropython/micropython-lib/blob/master/umqtt.robust/README.rst
## https://github.com/micropython/micropython-lib/blob/master/umqtt.robust/umqtt/robust.py

from umqtt import simple
from umqtt.simple import MQTTException
import ujson
from utime import sleep

import wifi

class MQTTClient(simple.MQTTClient):
    def set_last_will(self, topic, message, **kwargs):
        super().set_last_will(bytearray(topic), bytearray(message), **kwargs)
    
    def set_connected_callback(self, cb):
        self.connected_callback = cb
    
    def connect(self):
        print('MQTT Connect...')
        if wifi.connect(timeout=10):
            try:
                super().connect()
            except OSError as e:
                pass
            else:
                print('MQTT connected.')
                if hasattr(self, 'connected_callback') and self.connected_callback != None:
                    self.connected_callback()
                return True
        print('MQTT failed!')
        return False

    def publish(self, topic, message, reconnect=False, **kwargs):
        print('MQTT Publish...')
        print("%s => %s" % (topic, message))
        try:
            super().publish(bytearray(topic), bytearray(message), **kwargs)
        except (MQTTException, OSError, AttributeError) as e:
            if reconnect:
                print('MQTT Reconnecting...')
                if self.connect():
                    return self.publish(topic, message, **kwargs)
        else:
            print('MQTT publish sent.')
            sleep(0.5)
            return True
        print('MQTT publish failed!')
        return False

    def publish_json(self, topic, message, **kwargs):
        return self.publish(topic, ujson.dumps(message), **kwargs)
