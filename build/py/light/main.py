import config
from lib.state import State

state = State(
    automatic = True,
    brightness = config.INITIAL_BRIGHTNESS,
    light = False,
    motion = False,
)

from internet import Internet
internet = state.observer(Internet)

from light import Light
state.observer(Light, priority=True)

if config.BUTTON_ENABLED:
    from button import Button
    state.observer(Button)

if config.MOTION_SENSOR_ENABLED:
    from motion_detector import MotionDetector
    state.observer(MotionDetector)

    from automation import Automation
    state.observer(Automation, priority=True)

if config.BATTERY_ENABLED:
    from battery import Battery
    state.observer(Battery)

try:
    internet.wait_for_messages()
except KeyboardInterrupt:
    state.deinit()
