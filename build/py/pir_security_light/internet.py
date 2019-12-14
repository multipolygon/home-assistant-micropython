from lib import secrets
from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.binary_sensors.motion import MotionBinarySensor
from lib.home_assistant.light import Light
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.switch import Switch
from lib.home_assistant_mqtt import HomeAssistantMQTT
from lib.mqtt import MQTTClient
from lib.wifi import WiFi
import gc

class Internet():
    def __init__(self, state):
        print(HomeAssistant.UID)

        HomeAssistant.NAME = "Security Light"
        HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

        ha = HomeAssistantMQTT(WiFi, MQTTClient, secrets)
        self.ha = ha

        light = ha.register('Light', Light, { 'brightness': True })
        motion_sensor = ha.register('Motion', MotionBinarySensor)
        auto_mode = ha.register('Automatic', Switch)

        gc.collect()

        def publish_state(state):
            print('publish_state()')
            light.set_state(state.light)
            light.set_brightness_state(state.brightness)
            motion_sensor.set_state(state.motion)
            auto_mode.set_state(state.automatic_mode)
            ha.publish_state(reconnect=False)

        state.set_callback(publish_state, on=['light', 'motion'])

        def light_command(message):
            x = bytearray(light.PAYLOAD_ON) == message
            state.set(light = x, manual_override = x)

        ha.subscribe(light.command_topic(), light_command)

        def brightness_command(message):
            state.set(brightness = int(message))

        ha.subscribe(light.brightness_command_topic(), brightness_command)

        def auto_mode_command(message):
            state.set(automatic_mode = bytearray(auto_mode.PAYLOAD_ON) == message)

        ha.subscribe(auto_mode.command_topic(), auto_mode_command)

    def run(self):
        def loop():
            self.ha.wait_msg()

        self.ha.connect_and_loop(loop, status_led=status_led)
