from home_assistant.sensor import Sensor

class Humidity(Sensor):    
    DEV_CLA = 'humidity'
    UNIT = '%'
    ICON = 'mdi:water-percent'
