from machine import reset
from machine import unique_id
from sys import print_exception
from utime import sleep, ticks_ms, ticks_diff
import struct
import urandom

class HomeAssistantMQTT():
    def __init__(self, WiFi, MQTTClient, secrets):
        urandom.seed(struct.unpack('i', unique_id())[0] + ticks_ms())
        
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

        self.config_sent = False

        def mqtt_connected():
            print('MQTT Connected!')
            if not self.config_sent:
                self.config_sent = self.publish_config()
            if len(self.callbacks) > 0:
                ## TODO: Find the common root of all registered callback topics                
                for name, integration in self.integrations.items():
                    topic = integration.base_topic() + "/#"
                    print('MQTT Subscribe: %s' % topic)
                    self.mqtt.subscribe(bytearray(topic))
                    break

        self.mqtt.set_connected_callback(mqtt_connected)

    def register(self, name, Integration, config={}):
        self.integrations[name] = Integration(name=name, state=self.state)
        self.configs[name] = config

    def set_state(self, name, state):
        self.integrations[name].set_state(state)

    def publish_config(self):
        print("MQTT publish config")
        success = True
        for name, integration in self.integrations.items():
            success &= self.mqtt.publish_json(
                integration.config_topic(),
                integration.config(**self.configs[name]),
                retain=True
            )
        return success
        
    def publish_state(self):
        print("MQTT publish state")
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
        print('Add callback: %s' % topic)
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
                        print('Sleeping...')
                        sleep(urandom.getrandbits(6))

        except Exception as exception:
            print_exception(exception)
            if status_led:
                status_led.fast_blink()
            sleep(10)
            if status_led:
                status_led.off()
            reset()
        
