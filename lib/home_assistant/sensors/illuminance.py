from lib.home_assistant.sensor import Sensor

class IlluminanceSensor(Sensor):
    DEVICE_CLASS = "illuminance" # The current light level in lx or lm.
