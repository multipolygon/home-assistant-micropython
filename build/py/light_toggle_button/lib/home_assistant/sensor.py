from home_assistant.main import HA

class Sensor(HA):
    COMPNT = 'sensor'
    JSON_NS = 'sen'
    UNIT = None
    ICON = None

    def sub_cfg(self, exp_aft=None, frc_upd=True, icon=None, unit=None):
        return dict(
            dev_cla = self.DEV_CLA,
            exp_aft = exp_aft, ## seconds
            frc_upd = frc_upd,
            ic = icon if icon != None else self.ICON,
            stat_t = self.base_tpc(),
            unit_of_meas = unit if unit != None else self.UNIT,
            val_tpl = self.val_tpl(),
        )
