from lib.random import random_int
from sys import print_exception
from ujson import dumps as json
from umqtt.simple import MQTTClient
from utime import sleep
import gc
import machine
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
        self.attributes = {}
        self.publish_config_on_connect = True
        self.mqtt = None

    def mqtt_connect(self):
        self.mqtt_disconnect()

        self.mqtt = MQTTClient(
            wifi.mac(),
            self.secrets.MQTT_SERVER,
            user=bytearray(self.secrets.MQTT_USER),
            password=bytearray(self.secrets.MQTT_PASSWORD)
        )

        def _mqtt_receive(*args):
            self.mqtt_receive(*args)
        
        self.mqtt.set_callback(_mqtt_receive)

        self.mqtt.connect()

        sleep(1)
        
        self.mqtt_subscribe()

        sleep(1)
        
        if self.publish_config_on_connect:
            self.publish_config_on_connect = not(self.publish_config())
            
    def mqtt_disconnect(self):
        if self.mqtt != None:
            try:
                self.mqtt.disconnect()
            except:
                pass
            self.mqtt = None
        gc.collect()

    def mqtt_subscribe(self):
        gc.collect()
        n = len(self.callbacks)
        if n > 0:
            if n == 1:
                topic = list(self.callbacks.keys())[0]
            else:
                topic = ""
                topics = self.callbacks.keys()
                for i in range(min((len(s) for s in topics))):
                    chars = [s[i] for s in topics]
                    if chars.count(chars[0]) == n:
                        topic += chars[0]
                    else:
                        break
                topic += "#"
            gc.collect()
            t = bytearray(topic)
            gc.collect()
            self.mqtt.subscribe(t)

    def mqtt_receive(self, in_topic, message):
        gc.collect()
        try:
            for topic, callback in self.callbacks.items():
                if bytearray(topic) == in_topic:
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
        gc.collect()
        for name, integration in self.integrations.items():
            print(name)
            config = integration.config(**self.configs[name])
            gc.collect()
            config = json(config)
            gc.collect()
            config = bytearray(config)
            gc.collect()
            topic = bytearray(integration.config_topic())
            gc.collect()
            self.mqtt.publish(topic, config, retain=True)
            gc.collect()
            sleep(1)

    def set_attribute(self, key, value):
        self.attributes[key] = value
        
    def publish_state(self):
        if self.mqtt:
            for integration in self.integrations.values():
                gc.collect()

                self.attributes["IP"] = wifi.ip()
                self.attributes["MAC"] = wifi.mac()
                self.attributes["RSSI"] = wifi.rssi()
                integration.set_attr(self.attributes)

                gc.collect()

                state = bytearray(json(integration.state()))

                gc.collect()

                self.mqtt.publish(bytearray(integration.state_topic()), state)

                return True # Optimisation: Return on first item since they all share the same state
        return False

    def subscribe(self, topic, callback):
        self.callbacks[topic] = callback

    def wait_for_messages(self, status_led=None, connection_required=True):
        if connection_required:
            try:
                while True:
                    gc.collect()
                    self.mqtt.wait_msg()

            except Exception as exception:
                print_exception(exception)
                if status_led:
                    status_led.fast_blink()
                sleep(random_int(6))
                if status_led:
                    status_led.off()
                machine.reset()
                
        else:
            while True:
                try:
                    if wifi.is_connected():
                        print('WiFi connected.')
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
                    print_exception(exception)
                    self.mqtt_disconnect()
                sleep(random_int(8))
