from lib import secrets
from lib.esp8266.wemos.d1mini import status_led
from lib.home_assistant.main import HomeAssistant
from lib.home_assistant.sensor import Sensor
from lib.home_assistant_mqtt import HomeAssistantMQTT
from lib.umqtt_robust import MQTTClient
from lib.wifi import WiFi
from machine import Pin
from utime import sleep_ms, ticks_ms, ticks_diff
import config

################################################################################

print(HomeAssistant.UID)

HomeAssistant.NAME = "Flow Rate"
HomeAssistant.TOPIC_PREFIX = secrets.MQTT_USER

ha = HomeAssistantMQTT(WiFi, MQTTClient, secrets)

ha.register(
    'Flow Rate',
    Sensor,
    {
        'icon': 'mdi:gauge',
        'unit': 'count/min',
    }
)

def publish_state(value):
    ha.integrations['Flow Rate'].set_state(value)
    ha.publish_state()

################################################################################

pin = Pin(config.INPUT_PIN, mode=Pin.IN)

count = 0

def increment(_):
    global count
    count += 1

pin.irq(
    trigger=(Pin.IRQ_RISING if not(config.INPUT_INVERTED) else Pin.IRQ_FALLING),
    handler=increment
)
    
def loop():
    global count
    count = 0
    start_ms = ticks_ms()
    print('Counting...')
    while ticks_diff(ticks_ms(), start_ms) < config.SAMPLE_INTERVAL * 1000:
        sleep_ms(250)
    print('Count: %d' % count)
    if count != 0:
        publish_state(count)

################################################################################

ha.connect_and_loop(loop, status_led=status_led)
