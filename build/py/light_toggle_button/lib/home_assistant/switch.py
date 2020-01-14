from home_assistant.main import HA

class Switch(HA):
    COMPNT = 'switch'
    JSON_NS = 'sw'
    ON = 'ON'
    OFF = 'OFF'

    def set_state(self, val):
        return super().set_state(self.ON if val else self.OFF)
    
    def sub_cfg(self, opt=True, ret=True, icon=None):
        return dict(
            cmd_t = self.cmd_tpc(),
            stat_t = self.base_tpc(),
            val_tpl = self.val_tpl(),
            opt = opt,
            ret = ret,
            ic = icon,
        )
