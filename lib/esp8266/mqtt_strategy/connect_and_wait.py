from machine import reset
from sys import print_exception
from utime import sleep, ticks_ms, ticks_diff
import urandom

one_day = 24 * 60 * 60 # seconds

startup = ticks_ms()

def uptime():
    return ticks_diff(ticks_ms(), startup) // 1000 # seconds

def run(mqtt, status_led=None, daily_reset=True, connected_callback=None):
    connection_attempts = 0

    try:
        while True:
            if daily_reset and uptime() > one_day:
                raise Exception('Daily reset')
            
            if mqtt.is_connected():
                mqtt.wait_msg()

            else:
                if mqtt.connect(timeout=30):
                    connection_attempts = 0
                    if connected_callback:
                        connected_callback()
                    
                else:
                    if connection_attempts > 10:
                        raise Exception('Failed to connect')
                    connection_attempts += 1
                    print('Sleeping...')
                    sleep(urandom.getrandbits(4))

    except Exception as exception:
        print_exception(exception)
        if status_led:
            status_led.fast_blink()
        sleep(10)
        if status_led:
            status_led.off()
        reset()
