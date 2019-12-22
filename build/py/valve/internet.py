from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.mqtt import HomeAssistantMQTT
from lib.home_assistant.switch import Switch
from lib.home_assistant.sensors.battery import BatterySensor
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
        status_led.off()

        HomeAssistant.NAME = config.NAME
        HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

        self.ha = ha = HomeAssistantMQTT(secrets)

        valve = ha.register('Valve', Switch, icon = "mdi:water-pump")

        def valve_command(message):
            state.set(valve_open = message.decode('utf-8') == valve.PAYLOAD_ON)

        ha.subscribe(valve.command_topic(), valve_command)

        if config.BATTERY_ENABLED:
            battery = ha.register('Battery', BatterySensor)

        status_led.fast_blink()
        state.telemetry = ha.mqtt_connect_and_publish_config_fail_safe()
        status_led.off()

        self.publish_scheduled = False

        def publish_state(_):
            self.publish_scheduled = False
            valve.set_state(state.valve_open)
            if config.BATTERY_ENABLED and hasattr(state, 'battery'):
                ha.set_attr('battery', '%d%%' % state.battery)
                battery.set_state(state.battery)
            state.set(
                telemetry = ha.publish_state()
            )

        self.publish_state = publish_state

    def schedule_publish_state(self):
        if not self.publish_scheduled:
            self.publish_scheduled = True
            schedule(self.publish_state, None)

    def on_battery_level_change(self, state):
        self.schedule_publish_state()

    def on_valve_open_change(self, state):
        self.schedule_publish_state()

    def wait_for_messages(self):
        self.ha.wait_for_messages(status_led = status_led)

    def deinit(self):
        self.ha.mqtt_disconnect()
