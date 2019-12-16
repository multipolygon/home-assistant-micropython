from lib.esp8266.wemos.d1mini import pinmap

NAME = "Solar HWS"

THERMISTOR_ADC = pinmap.A0
SOLAR_PROBE_GPIO = pinmap.D5
TANK_PROBE_GPIO = pinmap.D6
PUMP_GPIO = pinmap.D8

PUMP_ON = 1
PUMP_OFF = 0

MAXIMUM_SOLAR_TEMPERATURE = 110
MAXIMUM_TANK_TEMPERATURE = 65

def pump_logic(state):
    if state.solar_temperature >= MAXIMUM_SOLAR_TEMPERATURE:
        return PUMP_OFF
        
    elif state.tank_temperature >= MAXIMUM_TANK_TEMPERATURE:
        return PUMP_OFF
        
    elif state.solar_temperature <= state.tank_temperature + 6:
        return PUMP_OFF
        
    elif state.solar_temperature >= state.tank_temperature + 12:
        return PUMP_ON

def pump_boost(state):
    if state.tank_temperature >= MAXIMUM_TANK_TEMPERATURE + 10:
        return PUMP_OFF

def solar_adc_to_temperature(adc):
    return (adc - 36.1997) / 6.26956

def tank_adc_to_temperature(adc):
    return (adc - 36.1997) / 6.26956

# def solar_adc_to_temperature(adc):
#     return (adc - 288.6) / 6.38

# def tank_adc_to_temperature(adc):
#     return (adc - 285.54) / 5.269
