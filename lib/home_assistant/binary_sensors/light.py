from lib.home_assistant.binary_sensor import BinarySensor

class LightBinarySensor(BinarySensor):
    DEVICE_CLASS = "light" # On means light detected, Off means no light
    
