from lib.home_assistant.sensor import Sensor

class SignalStrengthSensor(Sensor):
    DEVICE_CLASS = "signal_strength" # Signal strength in dB or dBm.
    UNIT_OF_MEASUREMENT = "dBm"
