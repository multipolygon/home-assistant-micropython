from lib.home_assistant.main import HomeAssistant

MODE_AUTO = "auto"
MODE_OFF = "off"
MODE_HEAT = "heat"

class Climate(HomeAssistant):
    COMPONENT = "climate"

    def set_mode(self, val):
        return super().set_state(val, key = "mode")

    def set_current_temperature(self, val):
        return super().set_state(val, key = "cur_temp")

    def set_temperature(self, val):
        return super().set_state(val, key = "tgt_temp")

    def set_action(self, val):
        return super().set_state(val, key = "act")

    def mode_command_topic(self):
        return self.component_base_topic() + "/mode"

    def temperature_command_topic(self):
        return self.component_base_topic() + "/temp"
    
    def component_config(self, min=0, max=40, retain=True):
        state_topic = self.shorten_topic(self.state_topic())
        
        return {
            "act_t": state_topic,
            "act_tpl": self.value_template(key = "act"),
            "curr_temp_t": state_topic,
            "curr_temp_tpl": self.value_template(key = "cur_temp"),
            "max_temp": max,
            "min_temp": min,
            "mode_cmd_t": self.shorten_topic(self.mode_command_topic()),
            "mode_stat_t": state_topic,
            "mode_stat_tpl": self.value_template(key = "mode"),
            "modes": [MODE_AUTO, MODE_OFF, MODE_HEAT],
            "precision": 1.0,
            "ret": retain,
            "temp_cmd_t": self.shorten_topic(self.temperature_command_topic()),
            "temp_stat_t": state_topic,
            "temp_stat_tpl": self.value_template(key = "tgt_temp"),
        }
