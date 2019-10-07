from lib.home_assistant.binary_sensor import BinarySensor

class PlugBinarySensor(BinarySensor):
    DEVICE_CLASS = "plug" # On means device is plugged in, Off means device is unplugged
