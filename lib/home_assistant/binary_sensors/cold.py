from lib.home_assistant.binary_sensor import BinarySensor

class ColdBinarySensor(BinarySensor):
    DEVICE_CLASS = "cold" # On means cold, Off means normal
