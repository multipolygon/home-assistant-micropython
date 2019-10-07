from lib.home_assistant.sensor import Sensor

class PowerSensor(Sensor):
    DEVICE_CLASS = "power" # Power in W or kW.
