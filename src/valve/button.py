from lib.button import Button as DebouncedButton
import config

class Button():
    def __init__(self, state):
        def on(_):
            state.set(valve_open = not(state.valve_open))

        self.button = DebouncedButton(config.BTN_GPIO, on, on_value=config.BTN_DOWN_VAL)

    def deinit(self):
        self.button.deinit()
