from lib.button import Button as DebouncedButton
import config

class Button():
    def __init__(self, state):
        self.state = state

    def start(self):
        def press(_):
            self.state.set(valve_open = not(self.state.valve_open))

        self.button = DebouncedButton(
            config.BTN_GPIO,
            press,
            on_value=config.BTN_DOWN_VAL
        )

    def stop(self):
        self.button.deinit()
