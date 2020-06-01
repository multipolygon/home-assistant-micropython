from lib.esp8266.wemos.d1mini import pinmap

NAME = 'Light'

#### LED ####

LED_GPIO = pinmap.LED

#### Light / Switch ####

## Change the component for Home Assistant:
COMPNT = 'light' # options: 'Light', 'Switch', None

## Relay shield is D1 by default:
GPIO = pinmap.D1

BRIGHTNESS = False

INIT_BRI = 100 # percent

#### Button ####

BTN = False

## Wemos 1-button shield is D3 by default:
BTN_GPIO = pinmap.D3

## Set to 0 for Wemos 1-button shield:
BTN_VAL = 0

#### Motion Sensor ####

MOTN = True

## Wemos PIR shield is D3 by default:
MOTN_GPIO = pinmap.D3

## Set to 1 for Wemos PIR Shield:
MOTN_VAL = 1

## Turn off light n-seconds after being turned on:
MOTN_TIME = 15 * 60 # seconds

#### Battery ####

BATT = False

BATT_ADC = pinmap.A0

## Update interval:
BATT_INT = 10 * 60 # seconds

## Disable light when battery below:
BATT_LOW = 10 # percent or None
