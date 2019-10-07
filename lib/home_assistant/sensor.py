from lib.home_assistant.main import HomeAssistant

class Sensor(HomeAssistant):
    COMPONENT = "sensor"
    DEVICE_CLASS = None
    UNIT_OF_MEASUREMENT = None
    ICON = None

    def name(self):
        return self._name or self.DEVICE_CLASS or self.COMPONENT

    def component_config(self, expire_after=None, force_update = True):
        return {
            "dev_cla": self.DEVICE_CLASS,
            "ic": self.ICON,
            "unit_of_meas": self.UNIT_OF_MEASUREMENT,
            "frc_upd": force_update,
            "exp_aft": expire_after, ## seconds
        }
