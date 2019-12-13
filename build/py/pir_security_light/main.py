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
pwm.set_duty_percent(config.INITIAL_BRIGHTNESS)
pwm.off()

def on_change(state_machine):
    state = state_machine.get_state()
    
    pwm.on() if state[0:2] == 'On' else pwm.off()
    
    light.set_state(state[0:2] == 'On')
    light.set_brightness_state(pwm.get_duty_percent())
    motion_sensor.set_state('MotionDetected' in state)
    automatic_switch.set_state('Auto' in state)

    schedule(publish_state, None)

state_machine = StateMachine(on_change)

################################################################################

def light_command(message):
    state_machine.trigger('light_%s' % ('on' if bytearray(light.PAYLOAD_ON) == message else 'off'))

ha.subscribe(light.command_topic(), light_command)

def brightness_command(message):
    pwm.set_duty_percent(int(message))
    on_change(state_machine)

ha.subscribe(light.brightness_command_topic(), brightness_command)

def automatic_switch_command(message):
    state_machine.trigger('automatic_%s' % ('on' if bytearray(automatic_switch.PAYLOAD_ON) == message else 'off'))

ha.subscribe(automatic_switch.command_topic(), automatic_switch_command)

################################################################################

def pir_on(*_):
    state_machine.trigger('motion_detected')

def pir_off(*_):
    state_machine.trigger('motion_clear')

Button(config.PIR_SENSOR_PIN, pir_on, pir_off, inverted=config.PIR_INVERTED)

################################################################################

def loop():
    ha.wait_msg()

ha.connect_and_loop(loop, status_led=status_led)
