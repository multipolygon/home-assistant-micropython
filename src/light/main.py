from lib.esp8266.home_assistant_mqtt import HomeAssistantMQTT
from lib.esp8266.mqtt_strategy.connect_and_wait import run
from lib.esp8266.pwm_pin import PWMPin
from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.light import Light
import config

ha = HomeAssistantMQTT("Light")
ha.register('light', Light, { 'brightness': config.BRIGHTNESS })
pwm_pin = PWMPin(pwm_enabled=config.BRIGHTNESS)
pwm_pin.off()

def send_state():
    ha.integrations['light'].set_state(pwm_pin.state)
    ha.integrations['light'].set_brightness_state(pwm_pin.pwm_duty)
    ha.send_state()

def command_received(message):
    print(message)
    if b'ON' == message:
        status_led.on()
        pwm_pin.on()
    elif b'OFF' == message:
        status_led.off()
        pwm_pin.off()
    send_state()

ha.subscribe(
    ha.integrations['light'].command_topic(),
    command_received
)

def brightness_command_received(message):
    duty = int(message)
    print("PWM: %d" % duty)
    pwm_pin.duty(duty)

if config.BRIGHTNESS:
    ha.subscribe(
        ha.integrations['light'].brightness_command_topic(),
        brightness_command_received
    )

run(ha)
