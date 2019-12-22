from lib.button import Button as DebouncedButton
import config

class Button():
    def __init__(self, state):
        def on(_):
            state.set(valve_open = not(state.valve_open))

        self.button = DebouncedButton(config.BUTTON_GPIO, on, on_value=config.BUTTON_DOWN_VALUE)

    def deinit(self):
        self.button.deinit()
