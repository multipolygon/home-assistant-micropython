from lib.home_assistant.binary_sensor import BinarySensor

class ConnectivityBinarySensor(BinarySensor):
    DEVICE_CLASS = "connectivity" # On means connected, Off means disconnected
