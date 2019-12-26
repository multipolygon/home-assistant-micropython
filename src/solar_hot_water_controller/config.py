from lib.esp8266.wemos.d1mini import pinmap

NAME = "Solar HWS"

SOLAR_GPIO = pinmap.D5
TANK_GPIO = pinmap.D6
PUMP_GPIO = pinmap.D8

ADC = pinmap.A0

PUMP_ON = 1
PUMP_OFF = 0

SOLAR_MAX_TEMP = 110
TANK_MAX_TEMP = 80
TANK_TARGET_TEMP = 65

FREQ = 5 # seconds
AVERAGE = 6

def pump_logic(state):
    if state.solar_temp >= SOLAR_MAX_TEMP:
        ## solar is too hot, do not want water to vaporise
        return PUMP_OFF
        
    elif state.tank_temp >= TANK_MAX_TEMP:
        ## safety cut off
        return PUMP_OFF
    
    elif state.tank_temp >= state.tank_target_temp:
        ## tank is hot enough
        return PUMP_OFF

    elif state.solar_temp >= 12 + state.tank_temp:
        ## solar is more than 12 deg hotter than the tank
        return PUMP_ON
        
    elif state.solar_temp <= 6 + state.tank_temp:
        ## solar is less than 6 deg hotter than the tank
        return PUMP_OFF

def pump_boost(state):
    if state.tank_temp >= TANK_MAX_TEMP:
        return PUMP_OFF
    
    elif state.tank_temp >= state.tank_target_temp + 5:
        return PUMP_OFF

    elif state.solar_temp <= state.tank_temp:
        return PUMP_OFF

    else:
        return PUMP_ON

def solar_adc_to_temp(adc):
    return (adc - 36.1997) / 6.26956

def tank_adc_to_temp(adc):
    return (adc - 36.1997) / 6.26956

# def solar_adc_to_temperature(adc):
#     return (adc - 288.6) / 6.38

# def tank_adc_to_temperature(adc):
#     return (adc - 285.54) / 5.269
