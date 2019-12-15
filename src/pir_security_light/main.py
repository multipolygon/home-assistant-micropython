from battery import Battery
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
    battery_percent = 0,
    battery_level = 0,
)

i = Internet(state)

Battery(state)

Light(state)

MotionDetector(state)

i.wait_for_messages()
