from lib.esp8266.wemos.d1mini import pinmap

#### PIR Sensor ####

## PIR shields are D3 by default
PIR_SENSOR_PIN = pinmap.D2

## If True, a button press will toggle the output pin. Set to False to always turn ON and never OFF. False is useful for PIR sensors.
PIR_INVERTED = True

#### Light ####

## Relay shield is D1 by default
PWM_PIN = pinmap.D1 

## If DIMMABLE, set initial brightness as percentage
INITIAL_BRIGHTNESS = 10

## Turn off light n-seconds after being turned on, None will disable
LIGHT_OFF_DELAY = 30 # seconds

## Turn off light n-seconds after motion detected
MOTION_LIGHT_OFF_DELAY = 30 # seconds
