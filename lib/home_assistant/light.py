from lib.home_assistant.main import HomeAssistant

CMD_KEY = "cmd"
BRI_KEY = "bri"

class Light(HomeAssistant):
    COMPONENT = "light"
    JSON_NAMESPACE = "lit"
    PAYLOAD_ON = STATE_ON = "ON"
    PAYLOAD_OFF = STATE_OFF = "OFF"

    def set_state(self, val):
        return super().set_state(self.STATE_ON if val else self.STATE_OFF, key = CMD_KEY)

    def set_brightness_state(self, val):
        return super().set_state(val, key = BRI_KEY)

    def brightness_command_topic(self):
        return "/".join((self.component_base_topic(), BRI_KEY))

    def component_config(self, optimistic=True, retain=True, brightness=False):
        config = {
            "cmd_t": self.command_topic(),
            "opt": optimistic,
            "ret": retain,
            "stat_t": self.state_topic(),
            "stat_val_tpl": self.value_template(key = CMD_KEY),
        }

        if brightness:
            self.merge_config(config, {
                "bri_cmd_t": self.brightness_command_topic(),
                "bri_scl": 100,
                "bri_stat_t": self.state_topic(),
                "bri_val_tpl": self.value_template(key = BRI_KEY),
            })

        return config
