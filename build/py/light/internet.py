from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.binary_sensors.motion import MotionBinarySensor
from lib.home_assistant.light import Light
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.mqtt import HomeAssistantMQTT
from lib.home_assistant.switch import Switch
from micropython import schedule
import config
import secrets
import wifi

class Internet():
    def __init__(self, state):
        print(HomeAssistant.UID)

        status_led.slow_blink()
        wifi.disable_access_point()
        wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
        status_led.fast_blink()

        HomeAssistant.NAME = config.NAME
        HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

        self.ha = ha = HomeAssistantMQTT(secrets)

        if config.LIGHT_ENABLED:
            light = ha.register('Light', Light, brightness = config.LIGHT_DIMMABLE)

            def light_command(message):
                state.set(light = message.decode('utf-8') == light.PAYLOAD_ON)

            ha.subscribe(light.command_topic(), light_command)

            if config.LIGHT_DIMMABLE:
                def brightness_command(message):
                    state.set(brightness = round(float(message)))

                ha.subscribe(light.brightness_command_topic(), brightness_command)

        if config.MOTION_SENSOR_ENABLED:
            motion_sensor = ha.register('Motion', MotionBinarySensor)

            if config.LIGHT_ENABLED:
                auto_switch = ha.register('Auto', Switch)

                def auto_switch_command(message):
                    state.set(automatic = message.decode('utf-8') == auto_switch.PAYLOAD_ON)

                ha.subscribe(auto_switch.command_topic(), auto_switch_command)

        if wifi.is_connected():
            try:
                state.telemetry = ha.mqtt_connect()
            except:
                pass

        status_led.off()

        ## Prevent publishing config in the future because it will fail with out-of-memory error:
        ha.publish_config_on_connect = False

        self.publish_scheduled = False

        def publish_state(_):
            self.publish_scheduled = False
            print('HA publish state.')
            if config.LIGHT_ENABLED:
                light.set_state(state.light)
                if config.LIGHT_DIMMABLE:
                    light.set_brightness_state(state.brightness)
            if config.MOTION_SENSOR_ENABLED:
                motion_sensor.set_state(state.motion)
                if config.LIGHT_ENABLED:
                    auto_switch.set_state(state.automatic)
            if config.BATTERY_ENABLED:
                ha.set_attr('battery', '%d%%' % state.battery)
            state.set(
                telemetry = ha.publish_state()
            )

        self.publish_state = publish_state

    def schedule_publish_state(self):
        if not self.publish_scheduled:
            self.publish_scheduled = True
            schedule(self.publish_state, None)

    def on_light_change(self, state):
        if config.LIGHT_ENABLED:
            self.schedule_publish_state()

    def on_motion_change(self, state):
        self.schedule_publish_state()

    def on_battery_change(self, state):
        self.schedule_publish_state()

    def wait_for_messages(self):
        self.ha.wait_for_messages(status_led = status_led)

    def deinit(self):
        self.ha.mqtt_disconnect()
