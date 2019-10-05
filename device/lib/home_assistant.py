## https://www.home-assistant.io/docs/mqtt/discovery/
## https://www.home-assistant.io/components/sensor/#device-class
## https://www.home-assistant.io/components/binary_sensor/#device-class
## Note to self, do not put any proceedural code or logic in this module!

import machine
import ubinascii
import version

MANUFACTURER = "Echidna"
MODEL = "ESP8266"
UID = ubinascii.hexlify(machine.unique_id()).decode("utf-8").upper()
MAC = UID
VERSION = version.build_date
TOPIC_PREFIX = None
DISCOVERY_PREFIX = "homeassistant"

def titlecase(s):
    return " ".join((i[0].upper() + i[1:] for i in s.replace('_', ' ').split()))

def underscore(s):
    return s.lower().replace(' ', '_')

class MQTTDiscovery():
    COMPONENT = "generic"
    
    def __init__(self, name=None, state={}):
        self._name = name
        self._state = state
        
        if not self.COMPONENT in state:
            state[self.COMPONENT] = {}
            
        if underscore(self.name()) in state[self.COMPONENT]:
            raise AttributeError('State name conflict!')
        else:
            state[self.COMPONENT][underscore(self.name())] = {
                "state": None,
                "meta": {},
            }

    def name(self):
        return self._name or self.COMPONENT

    def state(self):
        return self._state

    def set_state(self, new_state):
        self._state[self.COMPONENT][underscore(self.name())]["state"] = new_state
        return self._state

    def value_template(self):
        return "{{value_json.%s.%s.state}}" % (self.COMPONENT, underscore(self.name()))
        
    def set_attributes(self, new_attributes):
        self._state[self.COMPONENT][underscore(self.name())]["meta"] = new_attributes
        return self._state
    
    def json_attributes_template(self):
        return "{{value_json.%s.%s.meta|tojson}}" % (self.COMPONENT, underscore(self.name()))
    
    def full_name(self):
        return titlecase(" ".join((MANUFACTURER, MODEL, UID, self.name())))

    def topic_prefix(self):
        return TOPIC_PREFIX and (TOPIC_PREFIX + "/") or ""
    
    def config_topic(self):
        object_id = "_".join((MANUFACTURER, MODEL, UID))
        return self.topic_prefix() + "/".join((DISCOVERY_PREFIX, self.COMPONENT, object_id, self.name(), "config")).lower().replace(' ', '_')

    def base_topic(self):
        return self.topic_prefix() + "/".join((MANUFACTURER, MODEL, UID)).lower().replace(' ', '_')
    
    def state_topic(self):
        return self.base_topic() + "/state"

    def attributes_topic(self):
        return self.state_topic()
    
    def device(self):
        return {
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "identifiers": UID,
            "sw_version": VERSION,
            "connections": [["mac", MAC]],
        }

class Switch(MQTTDiscovery):
    COMPONENT = "switch"
    STATE_ON = "ON"
    STATE_OFF = "OFF"
    PAYLOAD_ON = "ON"
    PAYLOAD_OFF = "OFF"

    def set_state(self, new_state):
        self._state[self.COMPONENT][underscore(self.name())]["state"] = new_state and self.STATE_ON or self.STATE_OFF
        return self._state
    
    def command_topic(self):
        return self.base_topic() + "/command"
    
    def config(self):
        return {
            "name": self.full_name(),
            "command_topic": self.command_topic(),
            "state_topic": self.state_topic(),
            "value_template": self.value_template(),
            "optimistic": False,
            "retain": True,
        }

class GenericSensor(MQTTDiscovery):
    COMPONENT = "sensor"
    DEVICE_CLASS = None

    def name(self):
        return self._name or self.DEVICE_CLASS or self.COMPONENT

    def config(self, expire_after=None):
        return {
            "name": self.full_name(),
            "device_class": self.DEVICE_CLASS,
            "state_topic": self.state_topic(),
            "value_template": self.value_template(),
            "expire_after": expire_after, ## seconds
            "device": self.device(),
        }
    
class BatterySensor(GenericSensor):
    DEVICE_CLASS = "battery" # Percentage of battery that is left.

class HumiditySensor(GenericSensor):    
    DEVICE_CLASS = "humidity" # Percentage of humidity in the air.

    def config(self, expire_after=900):
        return {
            "name": self.full_name(),
            "icon": "mdi:water-percent",
            "device_class": self.DEVICE_CLASS,
            "unit_of_measurement": "%",
            "state_topic": self.state_topic(),
            "value_template": self.value_template(),
            "force_update": True,
            "expire_after": expire_after, ## seconds
            "device": self.device(),
        }

class IlluminanceSensor(GenericSensor):
    DEVICE_CLASS = "illuminance" # The current light level in lx or lm.

class SignalStrengthSensor(GenericSensor):
    DEVICE_CLASS = "signal_strength" # Signal strength in dB or dBm.
    
    def config(self, expire_after=900):
        return {
            "name": self.full_name(),
            "device_class": self.DEVICE_CLASS,
            "unit_of_measurement": "dBm",
            "state_topic": self.state_topic(),
            "value_template": self.value_template(),
            "force_update": True,
            "expire_after": expire_after, ## seconds
            "device": self.device(),
        }

class TemperatureSensor(GenericSensor):
    DEVICE_CLASS = "temperature" # Temperature in °C or °F.
    
    def config(self, expire_after=900):
        return {
            "name": self.full_name(),
            "icon": "mdi:thermometer",
            "device_class": self.DEVICE_CLASS,
            "unit_of_measurement": "°C",
            "state_topic": self.state_topic(),
            "value_template": self.value_template(),
            "force_update": True,
            "expire_after": expire_after, ## seconds
            "device": self.device(),
        }

class PowerSensor(GenericSensor):
    DEVICE_CLASS = "power" # Power in W or kW.

class PressureSensor(GenericSensor):    
    DEVICE_CLASS = "pressure" # Pressure in hPa or mbar.

class TimestampSensor(GenericSensor):
    DEVICE_CLASS = "timestamp" # Datetime object or timestamp string.
    
class BinarySensor(GenericSensor):
    COMPONENT = "binary_sensor"
    PAYLOAD_ON = "ON"
    PAYLOAD_OFF = "OFF"

    def set_state(self, new_state):
        self._state[self.COMPONENT][underscore(self.name())]["state"] = new_state and self.PAYLOAD_ON or self.PAYLOAD_OFF
        return self._state
    
    def config(self, off_delay=900):
        return {
            "name": self.full_name(),
            "device_class": self.DEVICE_CLASS,
            "state_topic": self.state_topic(),
            "value_template": self.value_template(),
            "json_attributes_topic": self.attributes_topic(),
            "json_attributes_template": self.json_attributes_template(),
            "device": self.device(),
            "off_delay": off_delay, ## seconds
        }
    
class BatteryBinarySensor(BinarySensor):
    DEVICE_CLASS = "battery" # On means low, Off means normal

class ColdBinarySensor(BinarySensor):
    DEVICE_CLASS = "cold" # On means cold, Off means normal

class ConnectivityBinarySensor(BinarySensor):
    DEVICE_CLASS = "connectivity" # On means connected, Off means disconnected

class DoorBinarySensor(BinarySensor):
    DEVICE_CLASS = "door" # On means open, Off means closed
    
class GarageBinarySensor(BinarySensor):
    DEVICE_CLASS = "garage_door" # On means open, Off means closed
    
class GasBinarySensor(BinarySensor):
    DEVICE_CLASS = "gas" # On means gas detected, Off means no gas (clear)
    
class HeatBinarySensor(BinarySensor):
    DEVICE_CLASS = "heat" # On means hot, Off means normal
    
class LightBinarySensor(BinarySensor):
    DEVICE_CLASS = "light" # On means light detected, Off means no light
    
class LockBinarySensor(BinarySensor):
    DEVICE_CLASS = "lock" # On means open (unlocked), Off means closed (locked)
    
class MoistureBinarySensor(BinarySensor):
    DEVICE_CLASS = "moisture" # On means moisture detected (wet), Off means no moisture (dry)
    
class MotionBinarySensor(BinarySensor):
    DEVICE_CLASS = "motion" # On means motion detected, Off means no motion (clear)
    
class MovingBinarySensor(BinarySensor):
    DEVICE_CLASS = "moving" # On means moving, Off means not moving (stopped)
    
class OccupancyBinarySensor(BinarySensor):
    DEVICE_CLASS = "occupancy" # On means occupied, Off means not occupied (clear)
    
class OpeningBinarySensor(BinarySensor):
    DEVICE_CLASS = "opening" # On means open, Off means closed
    
class PlugBinarySensor(BinarySensor):
    DEVICE_CLASS = "plug" # On means device is plugged in, Off means device is unplugged
    
class PowerBinarySensor(BinarySensor):
    DEVICE_CLASS = "power" # On means power detected, Off means no power
    
class PresenceBinarySensor(BinarySensor):
    DEVICE_CLASS = "presence" # On means home, Off means away
    
class ProblemBinarySensor(BinarySensor):
    DEVICE_CLASS = "problem" # On means problem detected, Off means no problem (OK)
    
class SafetyBinarySensor(BinarySensor):
    DEVICE_CLASS = "safety" # On means unsafe, Off means safe
    
class SmokeBinarySensor(BinarySensor):
    DEVICE_CLASS = "smoke" # On means smoke detected, Off means no smoke (clear)
    
class SoundBinarySensor(BinarySensor):
    DEVICE_CLASS = "sound" # On means sound detected, Off means no sound (clear)
    
class VibrationBinarySensor(BinarySensor):
    DEVICE_CLASS = "vibration" # On means vibration detected, Off means no vibration (clear)
    
class WindowBinarySensor(BinarySensor):
    DEVICE_CLASS = "window" # On means open, Off means closed
