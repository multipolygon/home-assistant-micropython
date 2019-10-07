from lib.home_assistant.binary_sensor import BinarySensor

class WindowBinarySensor(BinarySensor):
    DEVICE_CLASS = "window" # On means open, Off means closed
