from lib.home_assistant.binary_sensor import BinarySensor
 
class SmokeBinarySensor(BinarySensor):
    DEVICE_CLASS = "smoke" # On means smoke detected, Off means no smoke (clear)
