from home_assistant.sensor import Sensor

class Battery(Sensor):
    DEV_CLA = 'battery'
    UNIT = '%'
