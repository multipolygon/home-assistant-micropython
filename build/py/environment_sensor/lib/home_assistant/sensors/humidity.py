from lib.home_assistant.sensor import Sensor

class HumiditySensor(Sensor):    
    DEVICE_CLASS = "humidity" # Percentage of humidity in the air.
    UNIT_OF_MEASUREMENT = "%"
    ICON = "mdi:water-percent"
