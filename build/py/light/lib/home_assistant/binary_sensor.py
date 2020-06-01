from home_assistant.main import HA

class BinarySensor(HA):
    COMPNT = 'binary_sensor'
    JSON_NS = 'bin'
    ON = 'ON'
    OFF = 'OFF'

    def set_state(self, val):
        return super().set_state(self.ON if val else self.OFF)
    
    def sub_cfg(self, exp_aft=None, frc_upd=True, off_dly=None):
        return dict(
            dev_cla = self.DEV_CLA,
            exp_aft = exp_aft, ## seconds
            frc_upd = frc_upd,
            off_dly = off_dly, ## seconds
            stat_t = self.base_tpc(),
            val_tpl = self.val_tpl(),
        )
