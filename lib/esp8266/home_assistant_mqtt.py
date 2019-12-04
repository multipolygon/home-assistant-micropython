class HomeAssistantMQTT():
    def __init__(self, WiFi, MQTTClient, secrets):
        self.state = {}
        self.integrations = {}
        self.configs = {}
        self.callbacks = {}

        self.wifi = WiFi(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)

        self.mqtt = MQTTClient(
            self.wifi.mac(),
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
                "IP": self.wifi.ip(),
                "MAC": self.wifi.mac(),
                "RSSI": self.wifi.rssi(),
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
        if self.wifi.connect(timeout=timeout):
            return self.mqtt.connect()
        else:
            return False

    def is_connected(self):
        return self.mqtt.is_connected()

    def wait_msg(self):
        self.mqtt.wait_msg()
