from lib.esp8266.wemos.d1mini import pinmap

NAME = "Env Sensor"

INTERVAL = 600 # seconds

BATTERY_ENABLED = True

BATTERY_ADC = pinmap.A0

BATTERY_SENSOR = True

ANALOG_ENABLED = True

ANALOG_ADC = pinmap.A0
