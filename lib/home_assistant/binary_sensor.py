from lib.home_assistant.main import HomeAssistant

class BinarySensor(HomeAssistant):
    COMPONENT = "binary_sensor"
    PAYLOAD_ON = "ON"
    PAYLOAD_OFF = "OFF"

    def name(self):
        return self._name or self.DEVICE_CLASS or self.COMPONENT
    
    def set_state(self, new_state):
        return super().set_state(new_state and self.PAYLOAD_ON or self.PAYLOAD_OFF)
    
    def component_config(self, off_delay=900):
        return {
            "device_class": self.DEVICE_CLASS,
            "off_delay": off_delay, ## seconds
        }
