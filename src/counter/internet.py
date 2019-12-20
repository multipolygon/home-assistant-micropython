from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.mqtt import HomeAssistantMQTT
from lib.home_assistant.sensor import Sensor
from lib.home_assistant.sensors.battery import BatterySensor
from micropython import schedule
import config
import secrets
import wifi

AUTO_PUBLISH = ['count', 'battery']

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

        counter = ha.register(
            'GPIO%s' % config.GPIO,
            Sensor,
            unit = config.UNIT_OF_MEASUREMENT,
            icon = 'mdi:counter',
        )

        if config.BATTERY_ENABLED:
            battery_sensor = ha.register('Battery', BatterySensor)

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
            counter.set_state(state.count)
            if config.BATTERY_ENABLED:
                counter.set_attr('battery', '%d%%' % state.battery)
                battery_sensor.set_state(state.battery)
            state.set(
                telemetry = ha.publish_state()
            )

        self.publish_state = publish_state

    def on_state_change(self, state, changed):
        for item in AUTO_PUBLISH:
            if item in changed:
                if not self.publish_scheduled:
                    self.publish_scheduled = True
                    schedule(self.publish_state, None)
                break

    def wait_for_messages(self):
        self.ha.wait_for_messages(status_led = status_led)

    def deinit(self):
        self.ha.mqtt_disconnect()
