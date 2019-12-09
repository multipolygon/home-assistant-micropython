from lib.esp8266.wemos.d1mini import pinmap

#### Light ####

## Relay shield is D1 by default
OUTPUT_PIN = pinmap.D1 

## Register dimmable light with Home Assistant, subscribe to MQTT brightness commands and enable PWM on GPIO Pin:
DIMMABLE = False

## If DIMMABLE, set initial brightness between 0 and 1024
INITIAL_BRIGHTNESS = 1024

## Turn off light n minutes after being turned on, None will disable
OFF_DELAY = 15 * 60 # seconds

#### Button Switch ####

BUTTON_ENABLED = True

## 1-Button and PIR shields are D3 by default
BUTTON_PIN = pinmap.D3

## If True, a button press will toggle the output pin. Set to False to always turn ON and never OFF. False is useful for PIR sensors.
BUTTON_TOGGLE = False

## Set to True for 1-Button shield and False for PIR shield
BUTTON_INVERTED = False

#### Motion Sensor ###

## If BUTTON_PIN is a PIR shield, send "button" press events over MQTT
MOTION_SENSOR = True
