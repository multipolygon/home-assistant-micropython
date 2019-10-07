from lib.home_assistant.binary_sensor import BinarySensor

class PowerBinarySensor(BinarySensor):
    DEVICE_CLASS = "power" # On means power detected, Off means no power
