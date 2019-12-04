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
    JSON_NAMESPACE = None
    TOPIC_PREFIX = None
    
    def __init__(self, name=None, state={}):
        self._name = name
        self._state = state

    def name(self):
        return self._name or self.COMPONENT

    def slug(self):
        return self.name().lower().replace(' ', '_')

    def state(self):
        return self._state
    
    def set_state(self, val, attr="_"):
        ns = self.JSON_NAMESPACE or self.COMPONENT
        if ns not in self._state:
            self._state[ns] = {}
        if self.slug() not in self._state[ns]:
            self._state[ns][self.slug()] = {}
        self._state[ns][self.slug()][attr] = val
        return self._state

    def set_attr(self, val):
        self._state['attr'] = val
        return self._state

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
                "uniq_id": self.full_name(),
                "dev": self.device(),
            },
            self.component_config(**args)
        )

    def component_config(self, **args):
        return None
    
    def full_name(self):
        return " ".join((self.MANUFACTURER, self.MODEL, self.UID, self.name()))

    def topic_prefix(self):
        return self.TOPIC_PREFIX and (self.TOPIC_PREFIX + "/") or ""
    
    def base_topic(self):
        return self.topic_prefix() + "/".join((self.MANUFACTURER, self.MODEL, self.UID)).lower().replace(' ', '_')

    def component_base_topic(self):
        return self.base_topic() + "/".join(("", self.JSON_NAMESPACE or self.COMPONENT, self.slug()))
    
    def state_topic(self):
        return self.base_topic()
    
    def value_template(self, attr='_'):
        return "{{value_json.%s.%s.%s}}" % (self.JSON_NAMESPACE or self.COMPONENT, self.slug(), attr)

    def attributes_topic(self):
        return self.base_topic()

    def attributes_template(self):
        return "{{value_json.attr|tojson}}"

    def command_topic(self):
        return self.component_base_topic() + "/cmd"
    
    def device(self):
        return {
            "name": (self.NAME and (self.NAME + " ") or "") + self.UID,
            "mf": self.MANUFACTURER,
            "mdl": self.MODEL,
            "ids": self.UID,
            "sw": self.BUILD_DATE,
        }

    def merge_config(self, target, source):
        if target and source:
            for key in source.keys():
                if source[key] != None:
                    target[key] = source[key]
        return target
