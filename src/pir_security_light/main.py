from automation import Automation
from internet import Internet
from lib.state import State
from light import Light
from motion_detector import MotionDetector
import config

state = State(
    light = False,
    brightness = config.INITIAL_BRIGHTNESS,
    motion = False,
    automatic = True,
)

state.observer(Light)

state.observer(MotionDetector)

state.observer(Automation)

state.observer(Internet).wait_for_messages()
