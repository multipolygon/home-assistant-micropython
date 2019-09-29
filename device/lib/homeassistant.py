## https://www.home-assistant.io/docs/mqtt/discovery/
## https://www.home-assistant.io/components/sensor/#device-class
## https://www.home-assistant.io/components/binary_sensor/#device-class
## https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/umqtt/simple.py

## Note to self, do not put any proceedural code or logic in this module!

import machine
import ubinascii

BRAND = "Echidna"
UID = ubinascii.hexlify(machine.unique_id()).decode("utf-8").upper()
IDENT = "ESP8266_" + UID

class MQTT():
    def publish_config():
        pass

    def publish_state(value):
        pass

    def publish_attributes(attr):
        pass

class GenericSensor():
    DEFAULT_NAME = "generic"
    
    def __init__(self, name=None, brand=BRAND, ident=IDENT):
        self.name = name
        self.brand = brand
        self.ident = ident

        if self.name == None:
            self.name = self.DEFAULT_NAME

    def sensor_type(self):
        return "sensor"

    def base_topic(self):
        return "homeassistant/%s/%s_%s/%s" % (self.sensor_type(), self.brand.lower(), self.ident.lower(), self.name)
    
    def config_topic(self):
        return "%s/config" % self.base_topic()

    def state_topic(self):
        return "%s/state" % self.base_topic()
    
    def attributes_topic(self):
        return "%s/attributes" % self.base_topic()

    def device(self):
        return {
            "manufacturer": self.brand,
            "model": "Wemos D1 Mini",
            "identifiers": self.ident,
        }

    def config(self):
        return {
            "name": "%s %s %s" % (self.brand, self.ident, self.name),
            "state_topic": self.state_topic(),
            "device": self.device(),
        }

class StatusSensor(GenericSensor):
    DEFAULT_NAME = "status"
    
    def sensor_type(self):
        return "binary_sensor"

    def payload_on(self):
        return "ON"

    def payload_off(self):
        return "OFF"
    
    def config(self, off_delay=900):
        return {
            "name": "%s %s %s" % (self.brand, self.ident, self.name),
            "device_class": "connectivity",
            "state_topic": self.state_topic(),
            "payload_on": self.payload_on(),
            "payload_off": self.payload_off(),
            "json_attributes_topic": self.attributes_topic(),
            "device": self.device(),
            "off_delay": off_delay, ## seconds
        }
    
class WiFiSignalStrengthSensor(GenericSensor):
    DEFAULT_NAME = "wifi_signal_strength"
    
    def config(self, expire_after=900):
        return {
            "name": "%s %s %s" % (self.brand, self.ident, self.name),
            "device_class": "signal_strength",
            "unit_of_measurement": "dBm",
            "state_topic": self.state_topic(),
            "force_update": True,
            "expire_after": expire_after, ## seconds
            "device": self.device(),
        }
    
class TemperatureSensor(GenericSensor):
    DEFAULT_NAME = "temperature"
        
    def config(self, expire_after=900):
        return {
            "name": "%s %s %s" % (self.brand, self.ident, self.name),
            "icon": "mdi:thermometer",
            "device_class": "temperature",
            "unit_of_measurement": "°C",
            "state_topic": self.state_topic(),
            "force_update": True,
            "expire_after": expire_after, ## seconds
            "device": self.device(),
        }
