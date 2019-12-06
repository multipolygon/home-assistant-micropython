from lib.esp8266.wemos.d1mini import pinmap

#### Light ####

## Relay shield is D1 by default
OUTPUT_PIN = pinmap.D1 

# Register dimmable light with Home Assistant, subscribe to MQTT brightness commands and enable PWM on GPIO Pin:
DIMMABLE = True

#### Button Switch ####

BUTTON_ENABLED = False

## 1-Button and PIR shields are D3 by default
BUTTON_PIN = pinmap.D3

## If True, a button press will toggle the output pin. Set to False to always turn ON and never OFF. False is useful for PIR sensors.
BUTTON_TOGGLE = True

## Set to False for PIR shield
BUTTON_INVERTED = True
