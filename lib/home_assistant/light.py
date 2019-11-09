from lib.home_assistant.main import HomeAssistant

class Light(HomeAssistant):
    COMPONENT = "light"
    PAYLOAD_ON = STATE_ON = "ON"
    PAYLOAD_OFF = STATE_OFF = "OFF"

    def set_state(self, new_state):
        return super().set_state(new_state and self.STATE_ON or self.STATE_OFF)

    def config(self, optimistic=True, retain=True):
        return {
            "~": self.base_topic(),
            "name": self.full_name(),
            "stat_t": self.state_topic().replace(self.base_topic(), "~"),
            "stat_val_tpl": self.value_template(),
            "json_attr_t": self.attributes_topic().replace(self.base_topic(), "~"),
            "json_attr_tpl": self.attributes_template(),
            "cmd_t": self.command_topic().replace(self.base_topic(), "~"),
            "opt": optimistic,
            "ret": retain,
            "uniq_id": self.full_name(),
            "dev": self.device(),
        }

