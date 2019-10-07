from lib.home_assistant.binary_sensor import BinarySensor

class HeatBinarySensor(BinarySensor):
    DEVICE_CLASS = "heat" # On means hot, Off means normal
    
