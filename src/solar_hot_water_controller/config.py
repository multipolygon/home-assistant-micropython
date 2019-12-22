from lib.esp8266.wemos.d1mini import pinmap

NAME = "Solar HWS"

THERMISTOR_ADC = pinmap.A0
SOLAR_PROBE_GPIO = pinmap.D5
TANK_PROBE_GPIO = pinmap.D6
PUMP_GPIO = pinmap.D8

PUMP_ON = 1
PUMP_OFF = 0

UPDATE_INTERVAL = 10 # seconds

SOLAR_MAXIMUM_TEMPERATURE = 110

TANK_MAXIMUM_TEMPERATURE = 80
TANK_TARGET_TEMPERATURE = 65

AVERAGE = 6

def pump_logic(state):
    if state.solar_temperature >= SOLAR_MAXIMUM_TEMPERATURE:
        ## solar is too hot, do not want water to vaporise
        return PUMP_OFF
        
    elif state.tank_temperature >= TANK_MAXIMUM_TEMPERATURE:
        ## safety cut off
        return PUMP_OFF
    
    elif state.tank_temperature >= state.tank_target_temperature:
        ## tank is hot enough
        return PUMP_OFF

    elif state.solar_temperature >= 12 + state.tank_temperature:
        ## solar is more than 12 deg hotter than the tank
        return PUMP_ON
        
    elif state.solar_temperature <= 6 + state.tank_temperature:
        ## solar is less than 6 deg hotter than the tank
        return PUMP_OFF

def pump_boost(state):
    if state.tank_temperature >= TANK_MAXIMUM_TEMPERATURE:
        return PUMP_OFF
    
    elif state.tank_temperature >= state.tank_target_temperature + 5:
        return PUMP_OFF

    elif state.solar_temperature <= state.tank_temperature:
        return PUMP_OFF

    else:
        return PUMP_ON

def solar_adc_to_temperature(adc):
    return (adc - 36.1997) / 6.26956

def tank_adc_to_temperature(adc):
    return (adc - 36.1997) / 6.26956

# def solar_adc_to_temperature(adc):
#     return (adc - 288.6) / 6.38

# def tank_adc_to_temperature(adc):
#     return (adc - 285.54) / 5.269
