from lib.esp8266.wemos.d1mini import pinmap

NAME = "Flood Sensor"

RETAIN = ('enable',)

SENSOR_PIN = pinmap.D6

ALARM_PIN = pinmap.D1
BTN_PIN = pinmap.D3

ALARM_SLEEP = 10 * 60 # seconds
NORMAL_SLEEP = 30 * 60 # seconds

BATT_ADC = pinmap.A0
