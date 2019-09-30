from machine import ADC, Pin
from utime import sleep
import pinmap
import status_led
import oled
import secrets
import wifi
from umqtt_robust import MQTTClient
import home_assistant
import solar_hot_water_controller
import thermistor_adc

oled.write('POWER ON')

adc = ADC(pinmap.A0)
button = Pin(pinmap.D3, mode=Pin.IN)
probe_1 = Pin(pinmap.D5, mode=Pin.OUT)
probe_2 = Pin(pinmap.D6, mode=Pin.OUT)
relay = Pin(pinmap.D8, mode=Pin.OUT)

home_assistant.MAC = wifi.mac()
ha_status = home_assistant.ConnectivityBinarySensor("Status")
ha_wifi_signal_strength = home_assistant.SignalStrengthSensor()
ha_temperature = home_assistant.TemperatureSensor() 
ha_temperature_2 = home_assistant.TemperatureSensor('Temperature 2')
ha_relay = home_assistant.Switch('Relay')

mqtt = MQTTClient(home_assistant.MODEL + home_assistant.UID, secrets.MQTT_SERVER, user=secrets.MQTT_USER, password=secrets.MQTT_PASSWORD)

def mqtt_connected_callback():
    print('MQTT sending config...')
    mqtt.publish_json(ha_status.config_topic(), ha_status.config(), retain=True)
    mqtt.publish_json(ha_status.attributes_topic(), { "ip_address": wifi.ip(), "mac_address": wifi.mac() })
    mqtt.publish_json(ha_wifi_signal_strength.config_topic(), ha_wifi_signal_strength.config(), retain=True)
    mqtt.publish_json(ha_temperature.config_topic(), ha_temperature.config(), retain=True)
    mqtt.publish_json(ha_temperature_2.config_topic(), ha_temperature_2.config(), retain=True)
    mqtt.publish_json(ha_relay.config_topic(), ha_relay.config(), retain=True)
    print('MQTT config sent.')

mqtt.set_connected_callback(mqtt_connected_callback)
mqtt.set_last_will(ha_status.state_topic(), ha_status.PAYLOAD_OFF)

number_of_readings = 10
probe_readings = {}

def read_probe(id, loop):
    if id == 1:
        probe_1.on()
        probe_2.off()
    else:
        probe_1.off()
        probe_2.on()
    
    sleep(1) # Delay may allow to stabilise?

    try:
        n = loop % number_of_readings
        probe_readings[id-1][n] = adc.read()
    except KeyError:
        probe_readings[id-1] = [adc.read()] * number_of_readings

    print(probe_readings[id-1])
        
    return sum(probe_readings[id-1]) / number_of_readings

while True:
    status_led.on()
    oled.write('MQTT...')
    mqtt.connect()
    if wifi.is_connected():
        oled.write('WiFi%4d' % wifi.rssi())
        ip = wifi.ip()
        oled.write(ip[0:8])
        oled.write(ip[8:])
        if mqtt.is_connected():
            oled.write(home_assistant.UID)
        else:
            oled.write('MQTT Err')
    else:
        oled.write('No WiFi!')
    status_led.off()
    sleep(3)

    for loop in range(1000):
        print('')
        print(loop)
        status_led.on()

        adc1 = read_probe(1, loop)
        adc2 = read_probe(2, loop)

        t1 = thermistor_adc.temperature(adc1)
        t2 = thermistor_adc.temperature(adc2)

        solar_hot_water_controller.logic(t1, t2, relay)

        oled.write('%4s%4s' % (wifi.is_connected() and wifi.rssi() or 'Err', mqtt.is_connected() and 'OK' or 'Err'), False)
        oled.write('%4d%4d' % (adc1, adc2), False)
        oled.write('%4.0f%4.0f' % (t1, t2), False)
        oled.write('%8s' % (relay.value() and 'ON' or 'OFF'), True)

        if loop % 100 == 0:
            mqtt.publish(ha_status.state_topic(), ha_status.PAYLOAD_ON, reconnect=True)
            mqtt.publish(ha_wifi_signal_strength.state_topic(), str(wifi.rssi()))
            mqtt.publish(ha_temperature.state_topic(), "%.0f" % t1)
            mqtt.publish(ha_temperature_2.state_topic(), "%.0f" % t2)
            mqtt.publish(ha_relay.state_topic(), relay.value() and ha_relay.PAYLOAD_ON or ha_relay.PAYLOAD_OFF)
            
        status_led.off()

        sleep(1)
