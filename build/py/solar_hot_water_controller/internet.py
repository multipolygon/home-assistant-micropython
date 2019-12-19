from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.sensors.temperature import TemperatureSensor
from lib.home_assistant.climate import Climate, MODE_OFF, ALL_MODES
from lib.home_assistant.mqtt import HomeAssistantMQTT
from micropython import schedule
import config
import secrets
import wifi

class Internet():
    def __init__(self, state):
        print(HomeAssistant.UID)

        status_led.fast_blink()
        wifi.disable_access_point()
        wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)
        status_led.slow_blink()

        HomeAssistant.NAME = config.NAME
        HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

        self.ha = ha = HomeAssistantMQTT(secrets)

        controller = ha.register('Controller', Climate, max = config.TANK_MAXIMUM_TEMPERATURE)
        solar_temperature_sensor = ha.register('Solar', TemperatureSensor)
        
        def controller_mode_command(message):
            mode = message.decode('utf-8')
            if mode in ALL_MODES:
                state.set(mode = mode)

        ha.subscribe(controller.mode_command_topic(), controller_mode_command)

        def controller_temperature_command(message):
            state.set(tank_target_temperature = round(float(message)))

        ha.subscribe(controller.temperature_command_topic(), controller_temperature_command)

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
            controller.set_mode(state.mode)
            controller.set_target_temperature(state.tank_target_temperature)
            controller.set_current_temperature(state.tank_temperature)
            controller.set_action("off" if state.mode == MODE_OFF else ("heating" if state.pump else "idle"))
            solar_temperature_sensor.set_state(state.solar_temperature)
            state.set(
                telemetry = ha.publish_state()
            )

        self.publish_state = publish_state

    def on_state_change(self, state, changed):
        if not self.publish_scheduled:
            self.publish_scheduled = True
            schedule(self.publish_state, None)

    def wait_for_messages(self):
        self.ha.wait_for_messages(
            status_led = status_led,
            connection_required = False
        )
