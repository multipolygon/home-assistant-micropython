from machine import reset
from machine import unique_id
from sys import print_exception
from utime import sleep, ticks_ms, ticks_diff
import struct
import urandom
import gc

class HomeAssistantMQTT():
    def __init__(self, WiFi, MQTTClient, secrets):
        urandom.seed(struct.unpack('i', unique_id())[0] + ticks_ms())
        
        self.state = {}
        self.integrations = {}
        self.configs = {}
        self.callbacks = {}
        self.attributes = {}

        self.wifi = WiFi(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)

        self.mqtt = MQTTClient(
            self.wifi.mac(),
            secrets.MQTT_SERVER,
            user=bytearray(secrets.MQTT_USER),
            password=bytearray(secrets.MQTT_PASSWORD)
        )

        def mqtt_receive(in_topic, message):
            for topic, callback in self.callbacks.items():
                if bytearray(topic) == in_topic:
                    callback(message)
                    break

        self.mqtt.set_callback(mqtt_receive)

        self.send_config_on_connect = True

        def mqtt_subscribe():
            n = len(self.callbacks)
            if n > 0:
                if n == 1:
                    topic = list(self.callbacks.keys())[0]
                else:
                    topic = ""
                    topics = self.callbacks.keys()
                    for i in range(min([len(s) for s in topics])):
                        chars = [s[i] for s in topics]
                        if chars.count(chars[0]) == n:
                            topic += chars[0]
                        else:
                            break
                    topic += "#"
                gc.collect()
                self.mqtt.subscribe(bytearray(topic))

        def mqtt_connected():
            if self.send_config_on_connect:
                self.send_config_on_connect = not(self.publish_config())
            mqtt_subscribe()

        self.mqtt.set_connected_callback(mqtt_connected)

    def register(self, name, Integration, config={}):
        self.integrations[name] = Integration(name=name, state=self.state)
        self.configs[name] = config
        return self.integrations[name]

    def set_state(self, name, state):
        self.integrations[name].set_state(state)

    def publish_config(self):
        success = True
        for name, integration in self.integrations.items():
            gc.collect()
            success &= self.mqtt.publish_json(
                integration.config_topic(),
                integration.config(**self.configs[name]),
                retain=True
            )
            gc.collect()
        return success

    def set_attribute(self, key, value):
        self.attributes[key] = value
        
    def publish_state(self, reconnect=False):
        for integration in self.integrations.values():
            gc.collect()
            self.attributes["IP"] = self.wifi.ip()
            self.attributes["MAC"] = self.wifi.mac()
            self.attributes["RSSI"] = self.wifi.rssi()
            integration.set_attr(self.attributes)
            # Optimisation: Return on first item since they all share the same state:
            return self.mqtt.publish_json(
                integration.state_topic(),
                integration.state(),
                reconnect=reconnect
            )

    def subscribe(self, topic, callback):
        self.callbacks[topic] = callback
            
    def connect(self, timeout=30):
        if self.wifi.connect(timeout=timeout):
            return self.mqtt.connect()
        else:
            return False

    def is_connected(self):
        return self.mqtt.is_connected()

    def publish(self, *args, **kwargs):
        return self.mqtt.publish(*args, **kwargs)

    def wait_msg(self):
        self.mqtt.wait_msg()

    def check_msg(self):
        self.mqtt.check_msg()

    def connect_and_loop(self, callback, status_led=None, daily_reset=True, connected_callback=None):
        DAILY_RESET_INTERVAL = 24 * 60 * 60 # seconds
        connection_attempts = 0
        startup = ticks_ms()

        def uptime():
            return ticks_diff(ticks_ms(), startup) // 1000 # seconds

        try:
            while True:
                if daily_reset and uptime() > DAILY_RESET_INTERVAL:
                    raise Exception('Daily reset')

                if self.is_connected():
                    callback()

                else:
                    if self.connect(timeout=30):
                        connection_attempts = 0
                        if connected_callback:
                            connected_callback()

                    else:
                        if connection_attempts > 10:
                            raise Exception('Failed to connect')
                        connection_attempts += 1
                        sleep(urandom.getrandbits(6))

        except Exception as exception:
            print_exception(exception)
            if status_led:
                status_led.fast_blink()
            sleep(10)
            if status_led:
                status_led.off()
            reset()
        
