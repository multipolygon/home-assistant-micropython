## https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/umqtt/simple.py
## https://github.com/micropython/micropython-lib/blob/master/umqtt.robust/README.rst
## https://github.com/micropython/micropython-lib/blob/master/umqtt.robust/umqtt/robust.py

from sys import print_exception
from umqtt import simple
from umqtt.simple import MQTTException
from utime import sleep
import ujson

exceptions = (OSError, MQTTException, AttributeError)

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

    def reconnectable(self):
        try:
            return self._reconnectable
        except AttributeError:
            return False
    
    def connect(self):
        self._reconnectable = True
        if self.is_connected():
            print('MQTT already connected')
        else:
            print('MQTT connect...')
            try:
                self._is_connected = (super().connect() == 0)
            except exceptions as e:
                print_exception(e)
                self._is_connected = False
            if self.is_connected():
                print('MQTT connected.')
                if hasattr(self, 'connected_callback') and self.connected_callback != None:
                    self.connected_callback()
            else:
                print('MQTT failed!')
        return self.is_connected()

    def disconnect(self):
        self._reconnectable = False
        super().disconnect()
        return True

    def publish(self, topic, message, reconnect=False, **kwargs):
        # print('MQTT publish...')
        # print("%s => %s" % (topic, message))
        try:
            super().publish(bytearray(topic), bytearray(message), **kwargs)
        except exceptions as e:
            print_exception(e)
            self._is_connected = False
            if reconnect and self.reconnectable():
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

    def subscribe(self, topic, qos=0):
        try:
            super().subscribe(topic, qos)
            sleep(1)
            return True
        except exceptions as e:
            print_exception(e)
            self._is_connected = False
            return False

    def check_msg(self):
        try:
            super().check_msg()
            return True
        except exceptions as e:
            print_exception(e)
            self._is_connected = False
            return False

    def wait_msg(self):
        try:
            super().wait_msg()
            return True
        except exceptions as e:
            print_exception(e)
            self._is_connected = False
            return False
