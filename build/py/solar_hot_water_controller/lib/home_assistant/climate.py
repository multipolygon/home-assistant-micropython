from lib.home_assistant.main import HomeAssistant

MODE_AUTO = "auto"
MODE_OFF = "off"
MODE_HEAT = "heat"

class Climate(HomeAssistant):
    COMPONENT = "climate"

    def set_mode(self, val):
        return super().set_state(val, prop="mode")

    def set_current_temperature(self, val):
        return super().set_state(val, prop="temp")

    def set_action(self, val):
        return super().set_state(val, prop="act")

    def mode_command_topic(self):
        return self.component_base_topic() + "/mode"

    def temperature_command_topic(self):
        return self.component_base_topic() + "/temp"
    
    def component_config(self, initial=25, min=0, max=40, retain=True):
        state_topic = self.state_topic()
        
        return {
            "act_t": state_topic,
            "act_tpl": self.value_template(prop="act"),
            "curr_temp_t": state_topic,
            "curr_temp_tpl": self.value_template(prop="temp"),
            "init": initial, # temperature
            "max_temp": max,
            "min_temp": min,
            "mode_cmd_t": self.mode_command_topic(),
            "mode_stat_t": state_topic,
            "mode_stat_tpl": self.value_template(prop="mode"),
            "modes": [MODE_AUTO, MODE_OFF, MODE_HEAT],
            "precision": 1.0,
            "ret": retain,
            "temp_cmd_t": self.temperature_command_topic(),
        }
