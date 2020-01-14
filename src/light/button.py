from debounced_button import DebouncedButton
import config

class Button():
    def __init__(self, state):
        pass

    def start(self, state):
        def on(_):
            state.set(light = not(state.light))

        self.button = DebouncedButton(config.BTN_GPIO, on, on_value=config.BTN_VAL)

    def stop(self, state):
        self.button.deinit()
