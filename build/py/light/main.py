from lib import secrets
from lib.button import Button
from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.light import Light
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant_mqtt import HomeAssistantMQTT
from lib.pwm_pin import PWMPin
from lib.mqtt import MQTTClient
from lib.wifi import WiFi
import config

print(HomeAssistant.UID)

HomeAssistant.NAME = "Light"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

ha = HomeAssistantMQTT(WiFi, MQTTClient, secrets)

ha.register('Light', Light, { 'brightness': config.DIMMABLE })

pin_out = PWMPin(config.OUTPUT_PIN, pwm_enabled=config.DIMMABLE)
pin_out.off()

def publish_state():
    ha.integrations['Light'].set_state(pin_out.state)
    if config.DIMMABLE:
        ha.integrations['Light'].set_brightness_state(pin_out.pwm_duty)
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
    ha.integrations['Light'].command_topic(),
    command_received
)

if config.DIMMABLE:
    def brightness_command_received(message):
        duty = int(message)
        print("PWM: %d" % duty)
        pin_out.duty(duty)

    ha.subscribe(
        ha.integrations['Light'].brightness_command_topic(),
        brightness_command_received
    )

if config.BUTTON_ENABLED:
    def publish_command(_):
        print("MQTT publish command")
        ha.publish(
                ha.integrations['Light'].command_topic(),
                Light.PAYLOAD_ON if pin_out.state else Light.PAYLOAD_OFF,
                reconnect=True,
                retain=True
        )

    def button_press():
        state_was = pin_out.state

        if config.BUTTON_TOGGLE:
            pin_out.toggle()
        else:
            pin_out.on()

        status_led.set(pin_out.state)

        if state_was != pin_out.state:
            micropython.schedule(publish_command, None)

    Button(config.BUTTON_PIN, button_press, inverted=config.BUTTON_INVERTED)

def loop():
    print('Waiting...')
    ha.wait_msg()

print('Running...')
ha.connect_and_loop(loop, status_led=status_led)
