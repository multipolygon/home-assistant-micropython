from lib.home_assistant.main import HomeAssistant

class Light(HomeAssistant):
    COMPONENT = "light"
    PAYLOAD_ON = "ON"
    PAYLOAD_OFF = "OFF"
    STATE_ON = PAYLOAD_ON
    STATE_OFF = PAYLOAD_OFF

    def set_state(self, new_state):
        return super().set_state(new_state and self.STATE_ON or self.STATE_OFF)

    def config(self, optimistic=True, retain=True):
        return {
            "~": self.base_topic(),
            "name": self.full_name(),
            "stat_t": self.state_topic().replace(self.base_topic(), "~"),
            "stat_val_tpl": self.value_template(),
            "json_attr_t": self.attributes_topic().replace(self.base_topic(), "~"),
            "cmd_t": self.command_topic().replace(self.base_topic(), "~"),
            "opt": optimistic,
            "ret": retain,
            "dev": self.device(),
        }

