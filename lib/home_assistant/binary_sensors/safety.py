from lib.home_assistant.binary_sensor import BinarySensor

class SafetyBinarySensor(BinarySensor):
    DEVICE_CLASS = "safety" # On means unsafe, Off means safe
