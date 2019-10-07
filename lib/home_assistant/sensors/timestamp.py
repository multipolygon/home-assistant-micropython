from lib.home_assistant.sensor import Sensor

class TimestampSensor(Sensor):
    DEVICE_CLASS = "timestamp" # Datetime object or timestamp string.
