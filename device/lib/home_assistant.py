## https://www.home-assistant.io/docs/mqtt/discovery/
## https://www.home-assistant.io/components/sensor/#device-class
## https://www.home-assistant.io/components/binary_sensor/#device-class
## Note to self, do not put any proceedural code or logic in this module!

import machine
import ubinascii

MANUFACTURER = "Echidna"
MODEL = "ESP8266"
UID = ubinascii.hexlify(machine.unique_id()).decode("utf-8").upper()

class GenericSensor():
    sensor_type = "sensor"
    device_class = None
    
    def __init__(self, name=None, manufacturer=MANUFACTURER, model=MODEL, uid=UID):
        self.name = name
        self.manufacturer = manufacturer
        self.model = model
        self.uid = uid

        if self.name == None:
            if self.device_class != None:
                self.name = self.title(self.device_class)
            else:
                self.name = self.title(self.sensor_type)

    def title(self, s):
        return (s[0].upper() + s[1:]).replace('_', ' ')

    def base_topic(self):
        return ("homeassistant/%s/%s_%s_%s/%s" % (self.sensor_type, self.manufacturer, self.model, self.uid, self.name)).lower().replace(' ', '_')
    
    def config_topic(self):
        return "%s/config" % self.base_topic()

    def state_topic(self):
        return "%s/state" % self.base_topic()
    
    def attributes_topic(self):
        return "%s/attributes" % self.base_topic()

    def device(self):
        return {
            "manufacturer": self.manufacturer,
            "model": self.model,
            "identifiers": self.uid,
        }

    def full_name(self):
        return " ".join((self.manufacturer, self.model, self.uid, self.name))

    def config(self):
        return {
            "name": self.full_name(),
            "state_topic": self.state_topic(),
            "device": self.device(),
        }

class BatterySensor(GenericSensor):
    device_class = "battery" # Percentage of battery that is left.

class HumiditySensor(GenericSensor):    
    device_class = "humidity" # Percentage of humidity in the air.

class IlluminanceSensor(GenericSensor):
    device_class = "illuminance" # The current light level in lx or lm.

class SignalStrengthSensor(GenericSensor):
    device_class = "signal_strength" # Signal strength in dB or dBm.
    
    def config(self, expire_after=900):
        return {
            "name": self.full_name(),
            "device_class": self.device_class,
            "unit_of_measurement": "dBm",
            "state_topic": self.state_topic(),
            "force_update": True,
            "expire_after": expire_after, ## seconds
            "device": self.device(),
        }

class TemperatureSensor(GenericSensor):
    device_class = "temperature" # Temperature in °C or °F.
    
    def config(self, expire_after=900):
        return {
            "name": self.full_name(),
            "icon": "mdi:thermometer",
            "device_class": self.device_class,
            "unit_of_measurement": "°C",
            "state_topic": self.state_topic(),
            "force_update": True,
            "expire_after": expire_after, ## seconds
            "device": self.device(),
        }

class PowerSensor(GenericSensor):
    device_class = "power" # Power in W or kW.

class PressureSensor(GenericSensor):    
    device_class = "pressure" # Pressure in hPa or mbar.

class TimestampSensor(GenericSensor):
    device_class = "timestamp" # Datetime object or timestamp string.
    
class BinarySensor(GenericSensor):
    sensor_type = "binary_sensor"
    device_class = None
    payload_on = "ON"
    payload_off = "OFF"
    
    def config(self, off_delay=900):
        return {
            "name": self.full_name(),
            "device_class": self.device_class,
            "state_topic": self.state_topic(),
            "payload_on": self.payload_on,
            "payload_off": self.payload_off,
            "json_attributes_topic": self.attributes_topic(),
            "device": self.device(),
            "off_delay": off_delay, ## seconds
        }
    
class BatterySensor(BinarySensor):
    device_class = "battery" # On means low, Off means normal

class ColdSensor(BinarySensor):
    device_class = "cold" # On means cold, Off means normal

class ConnectivitySensor(BinarySensor):
    device_class = "connectivity" # On means connected, Off means disconnected

class DoorSensor(BinarySensor):
    device_class = "door" # On means open, Off means closed
    
class GarageSensor(BinarySensor):
    device_class = "garage_door" # On means open, Off means closed
    
class GasSensor(BinarySensor):
    device_class = "gas" # On means gas detected, Off means no gas (clear)
    
class HeatSensor(BinarySensor):
    device_class = "heat" # On means hot, Off means normal
    
class LightSensor(BinarySensor):
    device_class = "light" # On means light detected, Off means no light
    
class LockSensor(BinarySensor):
    device_class = "lock" # On means open (unlocked), Off means closed (locked)
    
class MoistureSensor(BinarySensor):
    device_class = "moisture" # On means moisture detected (wet), Off means no moisture (dry)
    
class MotionSensor(BinarySensor):
    device_class = "motion" # On means motion detected, Off means no motion (clear)
    
class MovingSensor(BinarySensor):
    device_class = "moving" # On means moving, Off means not moving (stopped)
    
class OccupancySensor(BinarySensor):
    device_class = "occupancy" # On means occupied, Off means not occupied (clear)
    
class OpeningSensor(BinarySensor):
    device_class = "opening" # On means open, Off means closed
    
class PlugSensor(BinarySensor):
    device_class = "plug" # On means device is plugged in, Off means device is unplugged
    
class PowerSensor(BinarySensor):
    device_class = "power" # On means power detected, Off means no power
    
class PresenceSensor(BinarySensor):
    device_class = "presence" # On means home, Off means away
    
class ProblemSensor(BinarySensor):
    device_class = "problem" # On means problem detected, Off means no problem (OK)
    
class SafetySensor(BinarySensor):
    device_class = "safety" # On means unsafe, Off means safe
    
class SmokeSensor(BinarySensor):
    device_class = "smoke" # On means smoke detected, Off means no smoke (clear)
    
class SoundSensor(BinarySensor):
    device_class = "sound" # On means sound detected, Off means no sound (clear)
    
class VibrationSensor(BinarySensor):
    device_class = "vibration" # On means vibration detected, Off means no vibration (clear)
    
class WindowSensor(BinarySensor):
    device_class = "window" # On means open, Off means closed
