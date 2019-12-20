from lib.random import random_int
from sys import print_exception
from uio import BytesIO
from umqtt.simple import MQTTClient
from utime import sleep
import gc
import machine
import ujson
import wifi

class MQTTCallbackException(Exception):
    pass

class HomeAssistantMQTT():
    def __init__(self, secrets):
        self.secrets = secrets
        self.state = {}
        self.integrations = {}
        self.configs = {}
        self.callbacks = {}
        self.publish_config_on_connect = True
        self.mqtt = None
        self.subscribe_topic = None

    def mqtt_connect(self):
        self.mqtt_disconnect()

        self.mqtt = MQTTClient(
            wifi.mac(),
            self.secrets.MQTT_SERVER,
            user=self.secrets.MQTT_USER.encode('utf-8'),
            password=self.secrets.MQTT_PASSWORD.encode('utf-8')
        )

        def _mqtt_receive(*args):
            self.mqtt_receive(*args)
        
        self.mqtt.set_callback(_mqtt_receive)

        self.mqtt.connect()

        sleep(0.5)
        
        if self.publish_config_on_connect:
            self.publish_config_on_connect = not(self.publish_config())
            
            sleep(0.5)
            
        self.mqtt_subscribe()

        sleep(0.5)
            
    def mqtt_disconnect(self):
        if self.mqtt != None:
            try:
                self.mqtt.disconnect()
            except:
                pass
            self.mqtt = None
        gc.collect()

    def mqtt_subscribe(self):
        if self.subscribe_topic != None:
            self.mqtt.subscribe(self.subscribe_topic)
            sleep(0.5)

    def mqtt_receive(self, in_topic, message):
        gc.collect()
        try:
            for topic, callback in self.callbacks.items():
                if topic == in_topic:
                    callback(message)
                    break
        except Exception as exception:
            print_exception(exception)
            raise MQTTCallbackException()

    def register(self, name, Integration, **config):
        self.integrations[name] = Integration(name=name, state=self.state)
        self.configs[name] = config
        return self.integrations[name]

    def publish_config(self):
        print('HA publish config.')
        for name, integration in self.integrations.items():
            print(name)
            gc.collect()
            topic = integration.config_topic().encode('utf-8')
            gc.collect()
            with BytesIO() as config:
                ujson.dump(integration.config(**self.configs[name]), config)
                gc.collect()
                self.mqtt.publish(topic, config.getvalue(), retain=True)
                sleep(0.5)
            gc.collect()

    def set_attr(self, key, val):
        for integration in self.integrations.values():
            integrations.set_attr(key, val)
            break ## All integrations share the same attributes
            
    def publish_state(self):
        if self.mqtt:
            for integration in self.integrations.values():
                gc.collect()
                topic = integration.state_topic().encode('utf-8')
                gc.collect()
                integration.set_attr("ip", wifi.ip())
                integration.set_attr("mac", wifi.mac())
                integration.set_attr("rssi", wifi.rssi())
                gc.collect()
                with BytesIO() as state:
                    ujson.dump(integration.state(), state)
                    integration.reset_state()
                    gc.collect()
                    self.mqtt.publish(topic, state.getvalue())
                    sleep(0.5)
                gc.collect()                
                return True # Return on first item since they all share the same state
        return False

    def subscribe(self, topic, callback):
        gc.collect()
        self.callbacks[topic.encode('utf-8')] = callback
        first = next(iter(self.callbacks))
        if len(self.callbacks) == 1:
            topic = first
        else:
            topic = b''
            for i, char in enumerate(first):
                for t in self.callbacks.keys():
                    if t[i] != char:
                        char = None
                        break
                if char == None:
                    break
                else:
                    topic += chr(char)
            topic += b'#'
        self.subscribe_topic = topic
        gc.collect()

    def wait_for_messages(self, status_led=None, connection_required=True):
        while True:
            try:
                if wifi.is_connected():
                    self.mqtt_connect()
                    while True:
                        gc.collect()
                        try:
                            self.mqtt.wait_msg()
                        except MQTTCallbackException:
                            pass
                else:
                    print('No WiFi!')
            except Exception as exception:
                print('MQTT Exception:')
                print_exception(exception)
                self.mqtt_disconnect()
            if connection_required:
                if status_led:
                    status_led.slow_blink()
                sleep(random_int(5))
                if status_led:
                    status_led.off()
            else:
                sleep(random_int(8))
