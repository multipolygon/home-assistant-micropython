from lib.home_assistant.binary_sensor import BinarySensor

class PresenceBinarySensor(BinarySensor):
    DEVICE_CLASS = "presence" # On means home, Off means away
