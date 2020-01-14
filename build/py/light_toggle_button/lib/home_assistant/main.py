## https://www.home-assistant.io/docs/mqtt/discovery/
## https://github.com/home-assistant/home-assistant/blob/master/homeassistant/components/mqtt/abbreviations.py
## https://www.home-assistant.io/components/sensor/#device-class
## https://www.home-assistant.io/components/binary_sensor/#device-class

from machine import unique_id
from ubinascii import hexlify
from uos import uname

UTF8 = 'utf-8'
ATTR = 'attr'

try:
    from version import build_date
except:
    build_date = '?'

class HA():
    NAME = None
    MANUF = 'Echidna'
    MDL = uname().sysname.upper()
    UID = hexlify(unique_id()).decode(UTF8).upper()
    BUILD = build_date
    DISCOV = 'homeassistant'
    DEV_CLA = None
    COMPNT = 'generic'
    JSON_NS = None
    
    def __init__(self, prefix=None, dev_name=None, name=None, key=None, state={}):
        self.prefix = prefix + '/' if prefix else ''
        self.dev_name = dev_name or 'Device'
        self.name = name or self.DEV_CLA or self.COMPNT
        self.key = key if key else self.name.lower().replace(' ', '_')
        self.state = state
        self.set_attr()

    def set_state(self, val, key=None):
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
        if ATTR not in self.state:
            self.state[ATTR] = {}
        if key != None:
            if val != None:
                self.state[ATTR][key] = val
            else:
                del self.state[ATTR][key]

    def cfg_tpc(self):
        object_id = '_'.join((self.MANUF, self.MDL, self.UID))
        return self.prefix + '/'.join((
            self.DISCOV,
            self.COMPNT,
            object_id,
            self.name,
            'config'
        )).lower().replace(' ', '_')

    def cfg(self, *arg, **kwarg):
        return self.short_cfg(
            name = self.ful_name(),
            json_attr_t = self.attr_tpc(),
            json_attr_tpl = self.attr_tpl(),
            uniq_id = self.ful_name(),
            dev = self.dev(),
            **self.sub_cfg(*arg, **kwarg),
        )

    def sub_cfg(self, *arg, **kwarg):
        return {}

    def short_tpc(self, topic):
        return topic.replace(self.base_tpc(), '~')

    def short_cfg(self, **cfg):
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
        return ' '.join((self.MDL, self.UID, self.dev_name))
    
    def ful_name(self):
        return ' '.join((self.ful_dev_name(), self.name))

    def base_tpc(self):
        return self.prefix + '/'.join((self.MANUF, self.MDL, self.UID)).lower().replace(' ', '_')

    def compnt_base_tpc(self):
        return self.base_tpc() + '/'.join(('', self.JSON_NS or self.COMPNT, self.key))

    def _tpl(self, s):
        return '{{value_json.%s}}' % s
    
    def val_tpl(self, key=None):
        key = ('.%s' % key) if key != None else ''
        return self._tpl('%s.%s%s' % (self.JSON_NS or self.COMPNT, self.key, key))

    def attr_tpc(self):
        return self.base_tpc()

    def attr_tpl(self):
        return self._tpl('attr|tojson')

    def cmd_tpc(self):
        return self.compnt_base_tpc() + '/cmd'
    
    def dev(self):
        return dict(
            name = self.ful_dev_name(),
            mf = self.MANUF,
            mdl = self.MDL,
            ids = self.UID,
            sw = self.BUILD,
        )
