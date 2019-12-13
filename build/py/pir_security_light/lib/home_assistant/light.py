from lib.home_assistant.main import HomeAssistant

class Light(HomeAssistant):
    COMPONENT = "light"
    PAYLOAD_ON = STATE_ON = "ON"
    PAYLOAD_OFF = STATE_OFF = "OFF"

    def set_state(self, new_state):
        return super().set_state(new_state and self.STATE_ON or self.STATE_OFF)

    def set_brightness_state(self, new_state):
        return super().set_state(new_state, attr="bri")

    def brightness_command_topic(self):
        return self.component_base_topic() + "/brightness"

    def config(self, optimistic=True, retain=True, brightness=False):
        c = {
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

        if brightness:
            c["bri_cmd_t"] = self.brightness_command_topic().replace(self.base_topic(), "~")
            c["bri_scl"] = 100
            c["bri_stat_t"] = self.state_topic().replace(self.base_topic(), "~")
            c["bri_val_tpl"] = self.value_template('bri')

        return c

