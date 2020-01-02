import lib.esp8266.wemos.d1mini.pinmap as pinmap

NAME = "Valve"

MOTOR_GPIO = pinmap.D1

CONTACT_GPIO = pinmap.D5

VALVE_OPEN_VAL = 0

#### Button ####

BTN = False

## Wemos 1-button shield is D3 by default:
BTN_GPIO = pinmap.D3

## Set to 0 for Wemos 1-button shield:
BTN_DOWN_VAL = 0

#### Battery ####

BATT = True

BATT_ADC = pinmap.A0

BATT_INT = 60 # seconds

BATT_LOW = None # 20 # percent or None

BATT_LOW_SLEEP = 30 * 60 # seconds
