from home_assistant.binary_sensor import BinarySensor

class Moisture(BinarySensor):
    DEVICE_CLASS = "moisture" # On means moisture detected (wet), Off means no moisture (dry)
    
