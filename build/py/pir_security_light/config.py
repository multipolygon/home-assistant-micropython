from lib.esp8266.wemos.d1mini import pinmap

NAME = "Security Floodlight"

#### PIR Sensor ####

## PIR shields are D3 by default
PIR_SENSOR_PIN = pinmap.D3

## Set to False for Wemos PIR Shield
PIR_INVERTED = False

#### Light ####

## Relay shield is D1 by default
# TODO: Use D8 (pull down)
PWM_PIN = pinmap.D1

## If DIMMABLE, set initial brightness as percentage
INITIAL_BRIGHTNESS = 10

## Turn off light n-seconds after being turned on, None will disable
LIGHT_OFF_DELAY = 10 # seconds

## Turn off light n-seconds after motion detected
MOTION_LIGHT_OFF_DELAY = 30 # seconds

#### Battery ####

LOW_BATTERY_DISABLE = None # 50 # percent or None
