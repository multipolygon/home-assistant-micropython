from lib.home_assistant.main import HomeAssistant

class Sensor(HomeAssistant):
    COMPONENT = "sensor"
    JSON_NAMESPACE = "sen"
    DEVICE_CLASS = None
    UNIT_OF_MEASUREMENT = None
    ICON = None

    def name(self):
        return self._name or self.DEVICE_CLASS or self.COMPONENT

    def component_config(self, expire_after=None, force_update=True, icon=None, unit=None):
        return {
            "dev_cla": self.DEVICE_CLASS,
            "exp_aft": expire_after, ## seconds
            "frc_upd": force_update,
            "ic": icon if icon != None else self.ICON,
            "stat_t": self.state_topic(),
            "unit_of_meas": unit if unit != None else self.UNIT_OF_MEASUREMENT,
            "val_tpl": self.value_template(),
        }
