from home_assistant.sensor import Sensor

class SignalStrength(Sensor):
    DEV_CLA = 'signal_strength'
    UNIT = 'dBm'
