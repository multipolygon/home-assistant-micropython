from home_assistant.main import HA

MODE_AUTO = 'auto'
MODE_OFF = 'off'
MODE_HEAT = 'heat'

MODES = [MODE_AUTO, MODE_OFF, MODE_HEAT]

MODE_KEY = 'mode'
TARG_KEY = 'targ'
TEMP_KEY = 'temp'
ACTN_KEY = 'actn'

class Climate(HA):
    COMPNT = 'climate'
    JSON_NS = 'cli'

    def set_mode(self, val):
        return super().set_state(val, key = MODE_KEY)

    def set_targ(self, val):
        return super().set_state(val, key = TARG_KEY)

    def set_temp(self, val):
        return super().set_state(val, key = TEMP_KEY)

    def set_actn(self, val):
        return super().set_state(val, key = ACTN_KEY)

    def mode_cmd_tpc(self):
        return self.compnt_base_tpc() + '/' + MODE_KEY

    def targ_cmd_tpc(self):
        return self.compnt_base_tpc() + '/' + TARG_KEY
    
    def sub_cfg(self, min=0, max=40, retain=True):
        tpc = self.short_tpc(self.base_tpc())
        
        return dict(
            act_t =  tpc,
            act_tpl = self.val_tpl(key = ACTN_KEY),
            curr_temp_t = tpc,
            curr_temp_tpl = self.val_tpl(key = TEMP_KEY),
            max_temp = max,
            min_temp = min,
            mode_cmd_t = self.short_tpc(self.mode_cmd_tpc()),
            mode_stat_t = tpc,
            mode_stat_tpl = self.val_tpl(key = MODE_KEY),
            modes = MODES,
            precision = 1.0,
            ret = retain,
            temp_cmd_t = self.short_tpc(self.targ_cmd_tpc()),
            temp_stat_t = tpc,
            temp_stat_tpl = self.val_tpl(key = TARG_KEY),
        )
