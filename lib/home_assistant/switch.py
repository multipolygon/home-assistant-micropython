from lib.home_assistant.main import HomeAssistant

class Switch(HomeAssistant):
    COMPONENT = "switch"
    STATE_ON = "ON"
    STATE_OFF = "OFF"
    PAYLOAD_ON = "ON"
    PAYLOAD_OFF = "OFF"

    def set_state(self, new_state):
        return super().set_state(new_state and self.STATE_ON or self.STATE_OFF)
    
    def component_config(self, optimistic=True, retain=True):
        return {
            "cmd_t": self.command_topic().replace(self.base_topic(), "~"),
            "opt": optimistic,
            "ret": retain,
        }
