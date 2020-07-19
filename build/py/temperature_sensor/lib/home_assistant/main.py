from uos import uname
from wifi import mac

UTF8 = 'utf-8'
ATTR = 'attr'

try:
    from version import build_date
except:
    build_date = '?'

class HA():
    # Home Assistant MQTT Discovery wrapper
    # See:
    # - https://www.home-assistant.io/docs/mqtt/discovery/
    # - https://github.com/home-assistant/home-assistant/blob/master/homeassistant/components/mqtt/abbreviations.py
    # - https://www.home-assistant.io/components/sensor/#device-class
    # - https://www.home-assistant.io/components/binary_sensor/#device-class
    NAME = None
    MANUF = 'HAMPy'
    MDL = uname().sysname.upper()
    UID = mac()
    BUILD = build_date
    DISCOV = 'homeassistant'
    DEV_CLA = None
    COMPNT = 'generic'
    JSON_NS = None
    
    def __init__(self, prefix=None, uid=None, dev_name=None, name=None, prim=False, key=None, state={}):
        # prefix: MQTT prefix
        # uid: Device unique id
        # dev_name: Device name
        # name: Component name
        # prim: Primary component
        # key: MQTT state object key (JSON)
        # state: Currnet state
        self.prefix = prefix + '/' if prefix else ''
        self.uid = uid or self.UID
        self.dev_name = dev_name or self.MDL
        self.name = name or self.DEV_CLA or self.COMPNT
        self.prim = prim
        self.key = key if key else self.name.lower().replace(' ', '_')
        self.state = state
        self.set_attr()

    def set_state(self, val, key=None):
        # Set State
        ns = self.JSON_NS or self.COMPNT
        if ns not in self.state:
            self.state[ns] = {}
        if key == None:
            self.state[ns][self.key] = val
        else:
            if self.key not in self.state[ns]:
                self.state[ns][self.key] = {}
            self.state[ns][self.key][key] = val

    def set_attr(self, key=None, val=None):
        # Set Attribute
        # Device meta-data eg WiFi RSSI or battery %.
        if ATTR not in self.state:
            self.state[ATTR] = {}
        if key != None:
            if val != None:
                self.state[ATTR][key] = val
            else:
                del self.state[ATTR][key]

    def cfg_tpc(self):
        # Config Topic
        return self.prefix + '/'.join((
            self.DISCOV,
            self.COMPNT,
            '_'.join((self.uid, self.dev_name)),
            self.name,
            'config'
        )).lower().replace(' ', '_')

    def cfg(self, *arg, **kwarg):
        # Config
        # JSON object sent over MQTT.
        return self.short_cfg(
            name = self.ful_name(),
            json_attr_t = self.attr_tpc(),
            json_attr_tpl = self.attr_tpl(),
            uniq_id = self.ful_name(),
            dev = self.dev(),
            **self.sub_cfg(*arg, **kwarg),
        )

    def sub_cfg(self, *arg, **kwarg):
        # Sub Config
        # Mix-in config for component subclass.
        # Component subclasses should implement this method.
        return {}

    def short_tpc(self, topic):
        # Short Topic
        # Replace topic prefix with ~ to reduce data sent over MQTT.
        return topic.replace(self.base_tpc(), '~')

    def short_cfg(self, **cfg):
        # Short Config
        # Shorten all topic strings (see short_tpc).
        for k, v in cfg.items():
            if v == None:
                del cfg[k]
            else:
                try:
                    cfg[k] = self.short_tpc(v)
                except:
                    pass
        cfg['~'] = self.base_tpc()
        return cfg

    def ful_dev_name(self):
        # Full Device Name
        # Identifies the device to Home Assistant.
        # (UID + Device Name).
        return ' '.join((self.uid, self.dev_name))
    
    def ful_name(self):
        # Full Name (of component)
        if self.prim:
            return self.ful_dev_name()
        else:
            return ' '.join((self.ful_dev_name(), self.name))

    def base_tpc(self):
        # Base Topic
        return self.prefix + '/'.join((self.dev_name, self.uid)).lower().replace(' ', '_')

    def cmd_base_tpc(self):
        # Command base topic
        return self.base_tpc() + '/cmd'

    def compnt_base_tpc(self):
        # Component Base Topic
        return self.cmd_base_tpc() + '/'.join(('', self.JSON_NS or self.COMPNT, self.key))

    def _tpl(self, s):
        # HA Template (Jinja2)
        # HA template to get a value from data object.
        return '{{value_json.%s}}' % s
    
    def val_tpl(self, key=None):
        # HA Value Temlate (Jinja2)
        key = ('.%s' % key) if key != None else ''
        return self._tpl('%s.%s%s' % (self.JSON_NS or self.COMPNT, self.key, key))

    def attr_tpc(self):
        # Attribute Topic
        return self.base_tpc()

    def attr_tpl(self):
        # Attribute Template
        return self._tpl('attr|tojson')

    def cmd_tpc(self):
        # Command Topic
        return self.compnt_base_tpc() + '/' + 'set'
    
    def dev(self):
        # Device
        # Meta data object.
        # HA will use this to group all components that belong to the same device and prevent duplicates.
        return dict(
            mf = self.MANUF,
            sw = self.BUILD,
            mdl = self.dev_name,
            ids = self.uid,
            name = self.ful_dev_name(),
        )
