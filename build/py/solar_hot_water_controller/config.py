from lib.esp8266.wemos.d1mini import pinmap

NAME = "Solar HWS"

THERMISTOR_ADC = pinmap.A0
SOLAR_PROBE_GPIO = pinmap.D5
TANK_PROBE_GPIO = pinmap.D6
PUMP_GPIO = pinmap.D8

def solar_adc_to_temperature(adc):
    return (adc - 36.1997) / 6.26956

def tank_adc_to_temperature(adc):
    return (adc - 36.1997) / 6.26956

# def solar_adc_to_temperature(adc):
#     return (adc - 288.6) / 6.38

# def tank_adc_to_temperature(adc):
#     return (adc - 285.54) / 5.269

def pump_logic(state):
    if state.solar_temperature >= 110:
        ## Too hot, don't want water to vaporise
        return False
        
    elif state.tank_temperature >= 65:
        return False
        
    elif state.solar_temperature - state.tank_temperature <= 6:
        return False
        
    elif solar_collector - storage_tank >= 12:
        return True
