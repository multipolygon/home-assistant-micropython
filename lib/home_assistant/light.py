from lib.home_assistant.main import HomeAssistant

class Light(HomeAssistant):
    COMPONENT = "light"
    PAYLOAD_ON = STATE_ON = "ON"
    PAYLOAD_OFF = STATE_OFF = "OFF"

    def set_state(self, val):
        return super().set_state(self.STATE_ON if val else self.STATE_OFF, key = "_")

    def set_brightness_state(self, val):
        return super().set_state(val, key = "bri")

    def brightness_command_topic(self):
        return self.component_base_topic() + "/bri"

    def component_config(self, optimistic=True, retain=True, brightness=False):
        config = {
            "cmd_t": self.command_topic(),
            "opt": optimistic,
            "ret": retain,
            "stat_t": self.state_topic(),
            "stat_val_tpl": self.value_template(key = "_"),
        }

        if brightness:
            self.merge_config(config, {
                "bri_cmd_t": self.brightness_command_topic(),
                "bri_scl": 100,
                "bri_stat_t": self.state_topic(),
                "bri_val_tpl": self.value_template(key = "bri"),
            })

        return config
