## https://www.home-assistant.io/docs/mqtt/discovery/
## https://github.com/home-assistant/home-assistant/blob/dev/homeassistant/components/mqtt/abbreviations.py
## https://www.home-assistant.io/components/sensor/#device-class
## https://www.home-assistant.io/components/binary_sensor/#device-class
## Note to self, do not put any proceedural code or logic in this module!

from machine import unique_id
from ubinascii import hexlify

try:
    from lib.version import build_date
except:
    build_date = '?'

class HomeAssistant():
    NAME = None
    MANUFACTURER = "Echidna"
    MODEL = "ESP8266"
    UID = hexlify(unique_id()).decode("utf-8").upper()
    BUILD_DATE = build_date
    DISCOVERY_PREFIX = "homeassistant"
    COMPONENT = "generic"
    TOPIC_PREFIX = None
    
    def __init__(self, name=None, state={}, attributes={}):
        self._name = name
        self._state = state
        self._attributes = attributes

    def name(self):
        return self._name or self.COMPONENT

    def slug(self):
        return self.underscore(self.name())

    def state(self):
        return self._state
    
    def attributes(self):
        return self._attributes
        
    def set_state(self, val):
        return self._set_obj(self._state, val)

    def set_attributes(self, val):
        return self._set_obj(self._attributes, val)

    def _set_obj(self, obj, val):
        if self.COMPONENT not in obj:
            obj[self.COMPONENT] = {}
        obj[self.COMPONENT][self.slug()] = val
        return obj

    def config_topic(self):
        object_id = "_".join((self.MANUFACTURER, self.MODEL, self.UID))
        return self.topic_prefix() + "/".join((self.DISCOVERY_PREFIX, self.COMPONENT, object_id, self.name(), "config")).lower().replace(' ', '_')

    def config(self, **args):
        return self.merge_config(
            {
                "~": self.base_topic(),
                "name": self.full_name(),
                "stat_t": self.state_topic().replace(self.base_topic(), "~"),
                "val_tpl": self.value_template(),
                "json_attr_t": self.attributes_topic().replace(self.base_topic(), "~"),
                "json_attr_tpl": self.attributes_template(),
                "unique_id": self.unique_id(),
                "dev": self.device(),
            },
            self.component_config(**args)
        )

    def component_config(self, **args):
        return {}
    
    def full_name(self):
        return self.titlecase(" ".join((self.MANUFACTURER, self.MODEL, self.UID, self.name())))

    def topic_prefix(self):
        return self.TOPIC_PREFIX and (self.TOPIC_PREFIX + "/") or ""
    
    def base_topic(self):
        return self.topic_prefix() + "/".join((self.MANUFACTURER, self.MODEL, self.UID)).lower().replace(' ', '_')
    
    def state_topic(self):
        return self.base_topic() + "/state"
    
    def value_template(self):
        return "{{value_json.%s and value_json.%s.%s}}" % (self.COMPONENT, self.COMPONENT, self.slug())

    def attributes_topic(self):
        return self.base_topic() + "/attr"
    
    def attributes_template(self):
        return "{{(value_json.%s and value_json.%s.%s or {})|tojson}}" % (self.COMPONENT, self.COMPONENT, self.slug())

    def unique_id(self):
        return self.base_topic() + "/" + "/".join((self.COMPONENT, self.slug()))
    
    def device(self):
        return {
            "name": (self.NAME and (self.NAME + " ") or "") + self.UID,
            "mf": self.MANUFACTURER,
            "mdl": self.MODEL,
            "ids": self.UID,
            "sw": self.BUILD_DATE,
        }

    def titlecase(self, s):
        return " ".join((i[0].upper() + i[1:] for i in s.replace('_', ' ').split()))

    def underscore(self, s):
        return s.lower().replace(' ', '_')
    
    def merge_config(self, target, source):
        for key in source.keys():
            if source[key] != None:
                target[key] = source[key]
        return target
