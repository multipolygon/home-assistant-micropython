from lib.home_assistant.main import HomeAssistant

class Sensor(HomeAssistant):
    COMPONENT = "sensor"
    DEVICE_CLASS = None
    UNIT_OF_MEASUREMENT = None
    ICON = None

    def name(self):
        return self._name or self.DEVICE_CLASS or self.COMPONENT

    def component_config(self, expire_after=None):
        return {
            "device_class": self.DEVICE_CLASS,
            "icon": self.ICON,
            "unit_of_measurement": self.UNIT_OF_MEASUREMENT,
            "force_update": True,
            "expire_after": expire_after, ## seconds
        }
