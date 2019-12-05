from lib import secrets
from lib.button import Button
from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant_mqtt import HomeAssistantMQTT
from lib.pwm_pin import PWMPin
from lib.umqtt_robust import MQTTClient
from lib.wifi import WiFi
import config

if config.LIGHT:
    from lib.home_assistant.light import Light
else:
    from lib.home_assistant.switch import Switch as Light

print(HomeAssistant.UID)

HomeAssistant.NAME = "Switch"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

ha = HomeAssistantMQTT(WiFi, MQTTClient, secrets)

ha.register('light', Light)

pin_out = PWMPin(config.OUTPUT_PIN, pwm_enabled=False)
pin_out.off()

def publish_state():
    ha.integrations['light'].set_state(pin_out.state)
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

def publish_command(_):
    print("MQTT publish command")
    ha.publish(
            ha.integrations['light'].command_topic(),
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

ha.subscribe(
    ha.integrations['light'].command_topic(),
    command_received
)

def loop():
    ha.wait_msg()

ha.connect_and_loop(loop, status_led=status_led)
