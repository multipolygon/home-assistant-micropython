from lib import secrets
from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.sensor import Sensor
from lib.home_assistant_mqtt import HomeAssistantMQTT
from lib.mqtt import MQTTClient
from lib.wifi import WiFi
from machine import Pin
from utime import sleep_ms, ticks_ms, ticks_diff
import config

################################################################################

print(HomeAssistant.UID)

HomeAssistant.NAME = "Counter"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

ha = HomeAssistantMQTT(WiFi, MQTTClient, secrets)

ha.set_attribute("Interval", config.SAMPLE_INTERVAL)

sensor = ha.register(
    'Counter',
    Sensor,
    {
        'icon': 'mdi:counter',
        'unit': 'count/min',
        # 'expire_after': config.SAMPLE_INTERVAL * 5,
    }
)

def publish_state(value):
    sensor.set_state(value)
    ha.publish_state()

################################################################################

pin = Pin(config.INPUT_PIN, mode=Pin.IN)

count = 0
active = True

def increment(_):
    global count
    count += 1
    status_led.on()

pin.irq(
    trigger=(Pin.IRQ_RISING if not(config.INPUT_INVERTED) else Pin.IRQ_FALLING),
    handler=increment
)
    
def loop():
    global count
    global active
    count = 0
    start_ms = ticks_ms()
    print('Counting...')
    while ticks_diff(ticks_ms(), start_ms) < config.SAMPLE_INTERVAL * 1000:
        sleep_ms(100)
    print('Count: %d' % count)
    if count != 0:
        active = True
    if active:
        publish_state(count)
    if count == 0:
        active = False
        status_led.off()

################################################################################

ha.connect_and_loop(loop, status_led=status_led)
