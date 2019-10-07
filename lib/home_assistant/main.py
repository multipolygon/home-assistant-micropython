## https://www.home-assistant.io/docs/mqtt/discovery/
## https://github.com/home-assistant/home-assistant/blob/dev/homeassistant/components/mqtt/abbreviations.py
## https://www.home-assistant.io/components/sensor/#device-class
## https://www.home-assistant.io/components/binary_sensor/#device-class
## Note to self, do not put any proceedural code or logic in this module!

from machine import unique_id
from network import WLAN
from ubinascii import hexlify

try:
    from lib.version import build_date
except:
    build_date = '?'

def mac():
    s = hexlify(WLAN().config('mac')).decode("utf-8").upper()
    return ":".join((s[i:i+2] for i in range(0,len(s),2)))

class HomeAssistant():
    MANUFACTURER = "Echidna"
    MODEL = "ESP8266"
    UID = hexlify(unique_id()).decode("utf-8").upper()
    MAC = mac()
    BUILD_DATE = build_date
    DISCOVERY_PREFIX = "homeassistant"
    COMPONENT = "generic"
    
    def __init__(self, name=None, state={}, topic_prefix=None):
        self._name = name
        self._state = state
        self.init_state()
        self._topic_prefix = topic_prefix

    def name(self):
        return self._name or self.COMPONENT

    def state(self):
        return self._state
    
    def init_state(self):
        if not self.COMPONENT in self._state:
            self._state[self.COMPONENT] = {}

        attr = self.underscore(self.name())
        if attr in self._state[self.COMPONENT]:
            raise AttributeError('State name conflict! %s %s' % (self.COMPONENT, attr))
        else:
            self._state[self.COMPONENT][attr] = {}

    def set_state(self, new_state):
        self._state[self.COMPONENT][self.underscore(self.name())]["state"] = new_state
        return self._state
        
    def set_attributes(self, new_attributes):
        self._state[self.COMPONENT][self.underscore(self.name())]["meta"] = new_attributes
        return self._state

    def config_topic(self):
        object_id = "_".join((self.MANUFACTURER, self.MODEL, self.UID))
        return self.topic_prefix() + "/".join((self.DISCOVERY_PREFIX, self.COMPONENT, object_id, self.name(), "config")).lower().replace(' ', '_')

    def config(self, **args):
        return self.merge_config(
            {
                "name": self.full_name(),
                "stat_t": self.state_topic(),
                "val_tpl": self.value_template(),
                "json_attr_t": self.attributes_topic(),
                "json_attr_tpl": self.json_attributes_template(),
                "dev": self.device(),
            },
            self.component_config(**args)
        )

    def component_config(self, **args):
        return {}
    
    def full_name(self):
        return self.titlecase(" ".join((self.MANUFACTURER, self.MODEL, self.UID, self.name())))

    def topic_prefix(self):
        return self._topic_prefix and (self._topic_prefix + "/") or ""
    
    def base_topic(self):
        return self.topic_prefix() + "/".join((self.MANUFACTURER, self.MODEL, self.UID)).lower().replace(' ', '_')
    
    def state_topic(self):
        return self.base_topic() + "/state"
    
    def value_template(self):
        return "{{value_json.%s.%s.state}}" % (self.COMPONENT, self.underscore(self.name()))

    def attributes_topic(self):
        return self.state_topic()
    
    def json_attributes_template(self):
        return "{{value_json.%s.%s.meta|tojson}}" % (self.COMPONENT, self.underscore(self.name()))
    
    def device(self):
        return {
            "mf": self.MANUFACTURER,
            "mdl": self.MODEL,
            "ids": self.UID,
            "sw": self.BUILD_DATE,
            "cns": [["mac", self.MAC]],
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
