from lib.home_assistant.sensor import Sensor

class TemperatureSensor(Sensor):
    DEVICE_CLASS = "temperature" # Temperature in °C or °F.
    UNIT_OF_MEASUREMENT = "°C"
    ICON = "mdi:thermometer"
