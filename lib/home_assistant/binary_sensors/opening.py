from lib.home_assistant.binary_sensor import BinarySensor
  
class OpeningBinarySensor(BinarySensor):
    DEVICE_CLASS = "opening" # On means open, Off means closed
