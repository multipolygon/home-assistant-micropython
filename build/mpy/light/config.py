from lib.esp8266.wemos.d1mini import pinmap

NAME = "Light"

#### Light ####

## Relay shield is D1 by default
LIGHT_GPIO = pinmap.D1

LIGHT_DIMMABLE = False

INITIAL_BRIGHTNESS = 100 # percent

#### Button ####

BUTTON_ENABLED = False

## Wemos 1-button shield is D3 by default
BUTTON_GPIO = pinmap.D3

## Set to 0 for Wemos 1-button shield
BUTTON_DOWN_VALUE = 0

#### Motion Sensor ####

MOTION_SENSOR_ENABLED = True

## Wemos PIR shield is D3 by default
MOTION_SENSOR_GPIO = pinmap.D3

## Set to 1 for Wemos PIR Shield
MOTION_DETECTED_VALUE = 1

## Turn off light n-seconds after being turned on
MOTION_LIGHT_OFF_DELAY = 10 # seconds

#### Battery ####

BATTERY_ENABLED = False

BATTERY_ADC = pinmap.A0

BATTERY_UPDATE_INTERVAL = 60 # seconds

BATTERY_LOW_DISABLE = None # percent or None
