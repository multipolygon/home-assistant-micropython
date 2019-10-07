from lib.home_assistant.sensor import Sensor

class PressureSensor(Sensor):    
    DEVICE_CLASS = "pressure" # Pressure in hPa or mbar.
