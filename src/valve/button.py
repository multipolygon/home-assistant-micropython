from debounced_button import DebouncedButton
import config

class Button():
    def __init__(self, state):
        pass

    def start(self, state):
        def press(_):
            state.set(valve_open = not(state.valve_open))

        self.button = DebouncedButton(
            config.BTN_GPIO,
            press,
            on_value=config.BTN_DOWN_VAL
        )

    def stop(self, state):
        self.button.deinit()
