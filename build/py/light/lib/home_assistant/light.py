from home_assistant.main import HA

CMD_KEY = 'set'
BRI_KEY = 'bri'

class Light(HA):
    COMPNT = 'light'
    JSON_NS = 'lit'
    ON = 'ON'
    OFF = 'OFF'

    def set_state(self, val):
        return super().set_state(self.ON if val else self.OFF, key = CMD_KEY)

    def set_bri(self, val):
        return super().set_state(val, key = BRI_KEY)

    def bri_cmd_tpc(self):
        return self.compnt_base_tpc() + '/' + BRI_KEY

    def sub_cfg(self, opt=True, ret=True, bri=False):
        return dict(
            cmd_t = self.cmd_tpc(),
            opt = opt,
            ret = ret,
            stat_t = self.base_tpc(),
            stat_val_tpl = self.val_tpl(key = CMD_KEY),
            **(dict(
                bri_cmd_t = self.bri_cmd_tpc(),
                bri_scl = 100,
                bri_stat_t = self.base_tpc(),
                bri_val_tpl = self.val_tpl(key = BRI_KEY),
            ) if bri else {}),
        )
