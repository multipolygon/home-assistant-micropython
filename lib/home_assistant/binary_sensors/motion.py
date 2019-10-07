from lib.home_assistant.binary_sensor import BinarySensor

class MotionBinarySensor(BinarySensor):
    DEVICE_CLASS = "motion" # On means motion detected, Off means no motion (clear)
