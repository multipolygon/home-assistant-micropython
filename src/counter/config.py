from lib.esp8266.wemos.d1mini import pinmap

NAME = "Counter"

## Wemos 1-button shield is D3 by default
GPIO = pinmap.D3

## Set to 0 for Wemos 1-button shield
GPIO_VAL = 0

FREQ = 60 # seconds

UNIT = 'count/min'

LED = pinmap.LED

#### Battery ####

BATT = True

BATT_ADC = pinmap.A0

BATT_INT = 60 # seconds
