from machine import ADC, Pin, reset
from utime import sleep, ticks_ms, ticks_diff
from sys import print_exception

from lib import secrets
from lib.esp8266 import wifi
from lib.esp8266.umqtt_robust import MQTTClient
from lib.esp8266.wemos.d1mini import pinmap
from lib.esp8266.wemos.d1mini import status_led

from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.light import Light

_24hrs = 24 * 60 * 60 # seconds

## Config ##

BRIGHTNESS = False

## Device ##

pin = Pin(pinmap.D1, mode=Pin.OUT) ## Relay default is D1
pwm_duty = 1024

if BRIGHTNESS:
    pwm = machine.PWM(pin, freq=1000)

def on(duty=None):
    global pwm_duty
    status_led.on()
    if BRIGHTNESS:
        if duty:
            pwm_duty = duty
        pwm.duty(pwm_duty)
    else:
        pin.on()
        
def off():
    status_led.off()
    if BRIGHTNESS:
        pwm.deinit()
    else:
        pin.off()

## Home Assistant ##

HomeAssistant.NAME = "Light"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

print(HomeAssistant.UID)

light = Light()

## MQTT ##

mqtt = MQTTClient(
    wifi.mac(),
    secrets.MQTT_SERVER,
    user=bytearray(secrets.MQTT_USER),
    password=bytearray(secrets.MQTT_PASSWORD)
)

def mqtt_send_config():
    print("MQTT send config")
    return mqtt.publish_json(light.config_topic(), light.config(brightness=BRIGHTNESS), retain=True)

def mqtt_send_state(clear_command=False):
    print("MQTT send state")
    light.set_attr({ "UID": HomeAssistant.UID, "IP": wifi.ip(), "MAC": wifi.mac(), "RSSI": wifi.rssi() })
    mqtt.publish_json(light.state_topic(), light.state(), reconnect=True)

def mqtt_receive(topic, message):
    global pwm_duty
    print("MQTT receive")
    if topic == bytearray(light.brightness_command_topic()):
        duty = int(message)
        print("PWM: %d" % duty)
        on(duty)
    elif topic == bytearray(light.command_topic()):
        if message == bytearray(light.STATE_ON):
            on()
            light.set_state(True)
            mqtt_send_state()
        elif message == bytearray(light.STATE_OFF):
            off()
            light.set_state(False)
            mqtt_send_state()

mqtt.set_callback(mqtt_receive)

def mqtt_connected():
    print("MQTT subscribe: " + light.command_topic())
    mqtt.subscribe(bytearray(light.command_topic()))
    if BRIGHTNESS:
        print("MQTT subscribe: " + light.brightness_command_topic())
        mqtt.subscribe(bytearray(light.brightness_command_topic()))

mqtt.set_connected_callback(mqtt_connected)

## Time ##

startup = ticks_ms()

def uptime():
    return ticks_diff(ticks_ms(), startup) // 1000 # seconds

## Main Loop ##

connection_attempts = 0
config_sent = False

try:
    while True:
        if not mqtt.is_connected():
            if mqtt.connect(timeout=30):
                connection_attempts = 0
            else:
                if connection_attempts > 10:
                    raise Exception('Connection')
                connection_attempts += 1
                sleep(5)

        elif uptime() > _24hrs:
            raise Exception('Daily reset')
            
        elif not(config_sent) and wifi.rssi() > -80:
            config_sent = mqtt_send_config()
            if config_sent:
                mqtt_send_state()

        else:
            mqtt.wait_msg()

except Exception as exception:
    print_exception(exception)
    for loop in range(30):
        status_led.led.value(loop % 2 == 0)
        sleep(0.5)

print("Reset")
reset()
