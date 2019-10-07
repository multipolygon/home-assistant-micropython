from lib.home_assistant.binary_sensor import BinarySensor
    
class GarageBinarySensor(BinarySensor):
    DEVICE_CLASS = "garage_door" # On means open, Off means closed
    
