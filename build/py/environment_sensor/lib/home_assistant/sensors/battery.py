from lib.home_assistant.sensor import Sensor

class BatterySensor(Sensor):
    DEVICE_CLASS = "battery" # Percentage of battery that is left.
    UNIT_OF_MEASUREMENT = "%"
