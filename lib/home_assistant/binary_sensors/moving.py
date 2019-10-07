from lib.home_assistant.binary_sensor import BinarySensor

class MovingBinarySensor(BinarySensor):
    DEVICE_CLASS = "moving" # On means moving, Off means not moving (stopped)
