## https://www.home-assistant.io/docs/mqtt/discovery/
## https://github.com/home-assistant/home-assistant/blob/master/homeassistant/components/mqtt/abbreviations.py
## https://www.home-assistant.io/components/sensor/#device-class
## https://www.home-assistant.io/components/binary_sensor/#device-class
## Note to self, do not put any proceedural code or logic in this module!

from machine import unique_id
from ubinascii import hexlify
from uos import uname

try:
    from lib.version import build_date
except:
    build_date = '?'

class HomeAssistant():
    NAME = None
    MANUFACTURER = "Echidna"
    MODEL = uname().sysname.upper()
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

    def reset_state(self):
        for key in self._state.keys():
            del self._state[key]
    
    def set_state(self, val, key=None):
        ns = self.JSON_NAMESPACE or self.COMPONENT
        if ns not in self._state:
            self._state[ns] = {}
        if key == None:
            self._state[ns][self.slug()] = val
        else:
            if self.slug() not in self._state[ns]:
                self._state[ns][self.slug()] = {}
            self._state[ns][self.slug()][key] = val

    def set_attr(self, key, val):
        if 'attr' not in self._state:
            self._state['attr'] = {}
        self._state['attr'][key] = val

    def config_topic(self):
        object_id = "_".join((self.MANUFACTURER, self.MODEL, self.UID))
        return self.topic_prefix() + "/".join((self.DISCOVERY_PREFIX, self.COMPONENT, object_id, self.name(), "config")).lower().replace(' ', '_')

    def config(self, *args, **argv):
        return self.shorten_config(
            self.merge_config(
                {
                    "name": self.full_name(),
                    "json_attr_t": self.attributes_topic(),
                    "json_attr_tpl": self.attributes_template(),
                    "uniq_id": self.full_name(),
                    "dev": self.device(),
                },
                self.component_config(*args, **argv)
            )
        )

    def shorten_topic(self, topic):
        return topic.replace(self.base_topic(), "~")

    def shorten_config(self, config):
        for key, val in config.items():
            if hasattr(val, 'replace'):
                config[key] = self.shorten_topic(val)
        config["~"] = self.base_topic()
        return config

    def component_config(self, **args):
        return None

    def device_name(self):
        return " ".join((self.MODEL, self.UID, self.NAME or self.MANUFACTURER))
    
    def full_name(self):
        return " ".join((self.device_name(), self.name()))

    def topic_prefix(self):
        return self.TOPIC_PREFIX and (self.TOPIC_PREFIX + "/") or ""
    
    def base_topic(self):
        return self.topic_prefix() + "/".join((self.MANUFACTURER, self.MODEL, self.UID)).lower().replace(' ', '_')

    def component_base_topic(self):
        return self.base_topic() + "/".join(("", self.JSON_NAMESPACE or self.COMPONENT, self.slug()))
    
    def state_topic(self):
        return self.base_topic()
    
    def value_template(self, key=None):
        key = (".%s" % key) if key != None else ""
        return "{{value_json.%s.%s%s}}" % (self.JSON_NAMESPACE or self.COMPONENT, self.slug(), key)

    def attributes_topic(self):
        return self.base_topic()

    def attributes_template(self):
        return "{{value_json.attr|tojson}}"

    def command_topic(self):
        return self.component_base_topic() + "/cmd"
    
    def device(self):
        return {
            "name": self.device_name(),
            "mf": self.MANUFACTURER,
            "mdl": self.MODEL,
            "ids": self.UID,
            "sw": self.BUILD_DATE,
        }

    def merge_config(self, target, source):
        if target and source:
            for key, val in source.items():
                if val != None:
                    target[key] = val
        return target
