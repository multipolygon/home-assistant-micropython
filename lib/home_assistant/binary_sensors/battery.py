from lib.home_assistant.binary_sensor import BinarySensor
    
class BatteryBinarySensor(BinarySensor):
    DEVICE_CLASS = "battery" # On means low, Off means normal
