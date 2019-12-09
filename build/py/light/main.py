from lib import secrets
from lib.button import Button
from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.binary_sensors.motion import MotionBinarySensor
from lib.home_assistant.light import Light
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant_mqtt import HomeAssistantMQTT
from lib.mqtt import MQTTClient
from lib.pwm_pin import PWMPin
from lib.wifi import WiFi
from machine import Timer
from micropython import schedule
import config

print(HomeAssistant.UID)

HomeAssistant.NAME = "Light"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

ha = HomeAssistantMQTT(WiFi, MQTTClient, secrets)

light = ha.register('Light', Light, { 'brightness': config.DIMMABLE })

pin_out = PWMPin(config.OUTPUT_PIN, pwm_enabled=config.DIMMABLE)
pin_out.off()

def publish_state(none=None):
    light.set_state(pin_out.state)
    if config.DIMMABLE:
        light.set_brightness_state(pin_out.pwm_duty)
    ha.publish_state()

def command_received(message):
    print(message)
    if b'ON' == message:
        status_led.on()
        pin_out.on()
    elif b'OFF' == message:
        status_led.off()
        pin_out.off()
    publish_state()

ha.subscribe(
    light.command_topic(),
    command_received
)

if config.OFF_DELAY:
    ha.set_attribute("Light Off Delay", config.OFF_DELAY)
    
    def off_delay_callback():
        status_led.off()
        schedule(publish_state, None)
    
    pin_out.set_off_delay(config.OFF_DELAY, off_delay_callback)

if config.DIMMABLE:
    pin_out.duty(config.INITIAL_BRIGHTNESS)
    
    def brightness_command_received(message):
        duty = int(message)
        print("PWM: %d" % duty)
        pin_out.duty(duty)

    ha.subscribe(
        ha.integrations['Light'].brightness_command_topic(),
        brightness_command_received
    )

if config.BUTTON_ENABLED:
    if config.MOTION_SENSOR:
        motion_sensor = ha.register('Motion', MotionBinarySensor, { 'off_delay': 60 })
        motion_sensor.set_state(False)
        motion_keep_alive = Timer(-1)
    
    def publish_command(*_):
        print("MQTT publish command")
        ha.publish(
                light.command_topic(),
                Light.PAYLOAD_ON if pin_out.state else Light.PAYLOAD_OFF,
                reconnect=True,
                retain=True
        )

    def button_on():
        state_was = pin_out.state

        if config.BUTTON_TOGGLE:
            pin_out.toggle()
        else:
            pin_out.on()

        status_led.set(pin_out.state)

        if config.MOTION_SENSOR:
            print('Motion Detected')
            motion_sensor.set_state(True)
            motion_keep_alive.init(
                period=30000,
                mode=Timer.PERIODIC,
                callback=lambda t:schedule(publish_state, None)
            )

        if state_was != pin_out.state:
            schedule(publish_command, None)
            ## Note, publish_command will also trigger publish_state
        elif config.MOTION_SENSOR:
            schedule(publish_state, None)

    def button_off():
        if config.MOTION_SENSOR:
            print('Motion Timeout')
            motion_sensor.set_state(False)
            motion_keep_alive.deinit()
            schedule(publish_state, None)

    Button(config.BUTTON_PIN, button_on, button_off, inverted=config.BUTTON_INVERTED)

def loop():
    print('Waiting...')
    ha.wait_msg()

print('Running...')
ha.connect_and_loop(loop, status_led=status_led)
