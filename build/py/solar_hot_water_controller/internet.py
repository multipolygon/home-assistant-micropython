from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.sensors.temperature import TemperatureSensor
from lib.home_assistant.switch import Switch
from lib.home_assistant_mqtt import HomeAssistantMQTT
from micropython import schedule
import config
import secrets
import wifi

wifi.disable_access_point()
wifi.connect(secrets.WIFI_NAME, secrets.WIFI_PASSWORD)

class Internet():
    def __init__(self, state):
        print(HomeAssistant.UID)

        HomeAssistant.NAME = config.NAME
        HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

        self.ha = ha = HomeAssistantMQTT(secrets)

        solar_temperature_sensor = ha.register('Solar', TemperatureSensor)
        tank_temperature_sensor = ha.register('Tank', TemperatureSensor)
        pump_switch = ha.register('Pump', Switch, { 'retain': False, 'optimistic': False })
        auto_switch = ha.register('Auto', Switch, { 'retain': True, 'optimistic': True })

        def pump_switch_command(message):
            state.set(pump = bytearray(pump_switch.PAYLOAD_ON) == message)

        ha.subscribe(pump_switch.command_topic(), pump_switch_command)
        
        def auto_switch_command(message):
            state.set(automatic = bytearray(auto_switch.PAYLOAD_ON) == message)

        ha.subscribe(auto_switch.command_topic(), auto_switch_command)

        self.publish_scheduled = False

        def publish_state(_):
            self.publish_scheduled = False
            solar_temperature_sensor.set_state(state.solar_temperature)
            tank_temperature_sensor.set_state(state.tank_temperature)
            pump_switch.set_state(state.pump == config.PUMP_ON)
            state.set(telemetry = ha.publish_state())

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
