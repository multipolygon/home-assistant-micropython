from lib import secrets
from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.binary_sensors.motion import MotionBinarySensor
from lib.home_assistant.light import Light
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.sensors.battery import BatterySensor
from lib.home_assistant.switch import Switch
from lib.home_assistant_mqtt import HomeAssistantMQTT
from micropython import schedule
import battery
import config
import wifi

wifi.disable_access_point()
wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)

class Internet():
    def __init__(self, state):
        print(HomeAssistant.UID)

        HomeAssistant.NAME = config.NAME
        HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

        self.ha = ha = HomeAssistantMQTT()

        light = ha.register('Light', Light, { 'brightness': True })
        motion_sensor = ha.register('Motion', MotionBinarySensor)
        auto_switch = ha.register('Automatic', Switch)
        battery_sensor = ha.register('Battery', BatterySensor)

        def light_command(message):
            state.set(light = bytearray(light.PAYLOAD_ON) == message)

        ha.subscribe(light.command_topic(), light_command)

        def brightness_command(message):
            state.set(brightness = int(message))

        ha.subscribe(light.brightness_command_topic(), brightness_command)

        def auto_switch_command(message):
            state.set(automatic = bytearray(auto_switch.PAYLOAD_ON) == message)

        ha.subscribe(auto_switch.command_topic(), auto_switch_command)

        ha.mqtt_connect()

        self.publish_scheduled = False

        def publish_state(_):
            self.publish_scheduled = False
            light.set_state(state.light)
            light.set_brightness_state(state.brightness)
            motion_sensor.set_state(state.motion)
            auto_switch.set_state(state.automatic)
            battery_sensor.set_state(battery.percent())
            ha.publish_state(reconnect=False)

        self.publish_state = publish_state

    def on_state_change(self, state, changed):
        if 'light' in changed or 'motion' in changed:
            if not self.publish_scheduled:
                self.publish_scheduled = True
                schedule(self.publish_state, None)

    def wait_for_messages(self):
        self.ha.wait_for_messages(status_led=status_led)
