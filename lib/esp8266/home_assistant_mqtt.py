from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.home_assistant.main import HomeAssistant

class HomeAssistantMQTT():
    def __init__(self, name=None, topic_prefix=None, send_config=True):
        print(HomeAssistant.UID)
        if name:
            HomeAssistant.NAME = "Light"
        HomeAssistant.TOPIC_PREFIX = topic_prefix if topic_prefix else secrets.MQTT_USER
        self.state = {}
        self.integrations = {}
        self.configs = {}
        self.callbacks = {}

        self.mqtt = MQTTClient(
            wifi.mac(),
            secrets.MQTT_SERVER,
            user=bytearray(secrets.MQTT_USER),
            password=bytearray(secrets.MQTT_PASSWORD)
        )

        def mqtt_receive(in_topic, message):
            print('MQTT Receive: %s' % in_topic)
            for topic, callback in self.callbacks.items():
                if bytearray(topic) == in_topic:
                    callback(message)
                    break

        self.mqtt.set_callback(mqtt_receive)

        def mqtt_connected():
            print('MQTT Connected!')
            if send_config:
                self.send_config()
            for topic, callback in self.callbacks.items():
                print('Subscribe: %s' % topic)
                self.mqtt.subscribe(bytearray(topic))

        self.mqtt.set_connected_callback(mqtt_connected)

    def register(self, name, Integration, config={}):
        self.integrations[name] = Integration(name=name, state=self.state)
        self.configs[name] = config

    def set_state(self, name, state):
        self.integrations[name].set_state(state)

    def send_config(self):
        print("MQTT send config")
        success = True
        for name, integration in self.integrations.items():
            success &= self.mqtt.publish_json(
                integration.config_topic(),
                integration.config(**self.configs[name]),
                retain=True
            )
        return success
        
    def send_state(self):
        print("MQTT send state")
        for name, integration in self.integrations.items():
            integration.set_attr({
                "UID": HomeAssistant.UID,
                "IP": wifi.ip(),
                "MAC": wifi.mac(),
                "RSSI": wifi.rssi(),
            })
            # Optimisation: Return on first item since they all share the same state:
            return self.mqtt.publish_json(
                integration.state_topic(),
                integration.state(),
                reconnect=True
            )

    def subscribe(self, topic, callback):
        self.callbacks[topic] = callback
            
    def connect(self, timeout=30):
        return True if self.mqtt.is_connected() else self.mqtt.connect(timeout=timeout)

    def is_connected(self):
        return self.mqtt.is_connected()

    def wait_msg(self):
        self.mqtt.wait_msg()
