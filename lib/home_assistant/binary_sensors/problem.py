from lib.home_assistant.binary_sensor import BinarySensor

class ProblemBinarySensor(BinarySensor):
    DEVICE_CLASS = "problem" # On means problem detected, Off means no problem (OK)
