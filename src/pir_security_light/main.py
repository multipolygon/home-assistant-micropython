from lib import secrets
from lib.button import Button
from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.binary_sensors.motion import MotionBinarySensor
from lib.home_assistant.light import Light
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.switch import Switch
from lib.home_assistant_mqtt import HomeAssistantMQTT
from lib.mqtt import MQTTClient
from lib.pwm_pin import PWMPin
from lib.wifi import WiFi
from micropython import schedule
import config
from state_machine import StateMachine
import gc

################################################################################

print(HomeAssistant.UID)

HomeAssistant.NAME = "Security Light"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

ha = HomeAssistantMQTT(WiFi, MQTTClient, secrets)

light = ha.register('Light', Light, { 'brightness': True })
motion_sensor = ha.register('Motion', MotionBinarySensor)
automatic_switch = ha.register('Automatic', Switch)

def publish_state(*_):
    ha.publish_state(reconnect=False)

gc.collect()

################################################################################

pwm = PWMPin(config.PWM_PIN, status_led=status_led)
pwm.off()

def on_change(state_machine):
    pwm.duty_percent(state_machine.brightness)
    pwm.on() if state_machine.light else pwm.off()
    
    light.set_state(state_machine.light)
    light.set_brightness_state(state_machine.brightness)
    motion_sensor.set_state(state_machine.motion)
    automatic_switch.set_state(state_machine.automatic)

    schedule(publish_state, None)

state_machine = StateMachine('Off', on_change)

################################################################################

def light_command(message):
    state_machine.event('light', bytearray(light.PAYLOAD_ON) == message)

ha.subscribe(light.command_topic(), light_command)

def brightness_command(message):
    state_machine.event('brightness', int(message))

ha.subscribe(light.brightness_command_topic(), brightness_command)

def automatic_switch_command(message):
    state_machine.event('automatic', bytearray(automatic_switch.PAYLOAD_ON) == message)

ha.subscribe(automatic_switch.command_topic(), automatic_switch_command)

################################################################################

def pir_on(*_):
    state_machine.event('motion', True)

def pir_off(*_):
    state_machine.event('motion', False)

Button(config.PIR_SENSOR_PIN, pir_on, pir_off, inverted=config.PIR_INVERTED)

################################################################################

print('Running...')

def loop():
    ha.wait_msg()

ha.connect_and_loop(loop, status_led=status_led)
