from lib.esp8266.wemos.d1mini import pinmap

NAME = "Valve"

BALL_VALVE_MOTOR_GPIO = pinmap.D1

BALL_VALVE_CONTACT_GPIO = pinmap.D5

BALL_VALVE_OPEN_VALUE = 0

#### Button ####

## Wemos 1-button shield is D3 by default:
BUTTON_GPIO = pinmap.D3

## Set to 0 for Wemos 1-button shield:
BUTTON_DOWN_VALUE = 0

#### Battery ####

BATTERY_ENABLED = True

BATTERY_ADC = pinmap.A0

BATTERY_UPDATE_INTERVAL = 60 * 60 # seconds

BATTERY_LOW_DISABLE = 10 # percent or None
