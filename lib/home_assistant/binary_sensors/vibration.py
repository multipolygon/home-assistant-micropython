from lib.home_assistant.binary_sensor import BinarySensor

class VibrationBinarySensor(BinarySensor):
    DEVICE_CLASS = "vibration" # On means vibration detected, Off means no vibration (clear)
