## https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/umqtt/simple.py
## https://github.com/micropython/micropython-lib/blob/master/umqtt.robust/README.rst
## https://github.com/micropython/micropython-lib/blob/master/umqtt.robust/umqtt/robust.py

from umqtt import simple
import ujson
from utime import sleep

from lib.esp8266 import wifi

class MQTTClient(simple.MQTTClient):
    def set_last_will(self, topic, message, **kwargs):
        super().set_last_will(bytearray(topic), bytearray(message), **kwargs)
    
    def set_connected_callback(self, cb):
        self.connected_callback = cb

    def is_connected(self):
        try:
            return self._is_connected
        except AttributeError:
            return False
    
    def connect(self):
        # print('MQTT connect...')
        self._is_connected = False
        if wifi.connect(timeout=10):
            try:
                super().connect()
            except Exception as e:
                # print(e)
                pass
            else:
                # print('MQTT connected.')
                self._is_connected = True
                if hasattr(self, 'connected_callback') and self.connected_callback != None:
                    self.connected_callback()
                return True
        # print('MQTT failed!')
        return False

    def publish(self, topic, message, reconnect=False, **kwargs):
        # print('MQTT publish...')
        # print("%s => %s" % (topic, message))
        try:
            super().publish(bytearray(topic), bytearray(message), **kwargs)
        except Exception as e:
            # print(e)
            self._is_connected = False
            if reconnect:
                # print('MQTT reconnecting...')
                if self.connect():
                    return self.publish(topic, message, **kwargs)
        else:
            # print('MQTT publish sent.')
            self._is_connected = True
            sleep(1)
            return True
        # print('MQTT publish failed!')
        return False

    def publish_json(self, topic, message, **kwargs):
        return self.publish(topic, ujson.dumps(message), **kwargs)

    def set_last_will(self, topic, message, **kwargs):
        return super().set_last_will(bytearray(topic), bytearray(message), **kwargs)
        
    def set_last_will_json(self, topic, message, **kwargs):
        return self.set_last_will(topic, ujson.dumps(message), **kwargs)
