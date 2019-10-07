from lib.home_assistant.binary_sensor import BinarySensor

class GasBinarySensor(BinarySensor):
    DEVICE_CLASS = "gas" # On means gas detected, Off means no gas (clear)
    
