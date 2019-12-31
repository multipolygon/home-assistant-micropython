from home_assistant.sensor import Sensor

class Temperature(Sensor):
    DEV_CLA = 'temperature'
    UNIT = '°C'
    ICON = 'mdi:thermometer'
