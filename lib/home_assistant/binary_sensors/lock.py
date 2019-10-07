from lib.home_assistant.binary_sensor import BinarySensor

class LockBinarySensor(BinarySensor):
    DEVICE_CLASS = "lock" # On means open (unlocked), Off means closed (locked)
    
