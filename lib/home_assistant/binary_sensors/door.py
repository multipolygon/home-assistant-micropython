from lib.home_assistant.binary_sensor import BinarySensor

class DoorBinarySensor(BinarySensor):
    DEVICE_CLASS = "door" # On means open, Off means closed
