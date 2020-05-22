from lib.esp8266.wemos.d1mini import pinmap

NAME = "Water Sensor"

RETAIN = ['enable', 'water']

OUT_PIN = pinmap.D2
IN_PIN = pinmap.D8 # pull down

ALARM_PIN = pinmap.D1

ALARM_SLEEP = 10 * 60 # seconds
NORMAL_SLEEP = 30 * 60 # seconds

BATT_ADC = pinmap.A0
