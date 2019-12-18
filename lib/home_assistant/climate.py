from lib.home_assistant.main import HomeAssistant

MODE_AUTO = "auto"
MODE_OFF = "off"

class Climate(HomeAssistant):
    COMPONENT = "climate"

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
            "ret": retain,
            "init": initial, # temperature
            "curr_temp_t": state_topic,
            "curr_temp_tpl": self.value_template(prop="temp"),
            "act_t": state_topic,
            "act_tpl": self.value_template(prop="act"),
            "mode_cmd_t": self.mode_command_topic(),
            "modes": [MODE_AUTO, MODE_OFF],
            "temp_cmd_t": self.temperature_command_topic(),
            "precision": 1.0,
            "min_temp": min,
            "max_temp": max,
        }
