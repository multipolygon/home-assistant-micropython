from lib.esp8266.wemos.d1mini import pinmap

NAME = "Counter"

## Wemos 1-button shield is D3 by default
GPIO = pinmap.D3

## Set to 0 for Wemos 1-button shield
GPIO_VALUE = 0

INTERVAL = 60 # seconds

UNIT_OF_MEASUREMENT = 'count/min'

LED = pinmap.LED

#### Battery ####

BATTERY_ENABLED = False

BATTERY_ADC = pinmap.A0

BATTERY_UPDATE_INTERVAL = 60 * 60 # seconds
