from internet import Internet
from lib.state import State
from light import Light
from motion_detector import MotionDetector
import config

state = State(
    light = False,
    brightness = config.INITIAL_BRIGHTNESS,
    motion = False,
    automatic_mode = True,
    manual_override = False,
)

Light(state)

MotionDetector(state)

Internet(state).wait_for_messages()
