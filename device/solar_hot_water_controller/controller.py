from utime import ticks_ms, ticks_diff

MAX_DUTY_CYCLE = 5 # minutes
FAILURE_DELAY = 60 # minutes

NORMAL = ON = TURN_ON = STAY_ON = True
FAIL = OFF = TURN_OFF = STAY_OFF = False

last_change = ticks_ms()
operating_mode = NORMAL

def timer():
    return ticks_diff(ticks_ms(), last_change) / 1000 / 60 # minutes

def logic(solar_collector, storage_tank, current_state):
    global last_change
    global operating_mode

    ## Detect and set failure states ##
    
    if operating_mode == NORMAL:
        if current_state == ON and timer() > MAX_DUTY_CYCLE:
            operating_mode = FAIL
            
            
    elif operating_mode == FAIL:
        if current_state == OFF and timer() > FAILURE_DELAY:
            operating_mode = NORMAL

    ## Turn pump on and off ##
            
    if operating_mode == NORMAL:
        temperature_difference = solar_collector - storage_tank

        if current_state == OFF:
            new_state = TURN_ON if storage_tank < 60 and temperature_difference > 12 else STAY_OFF
            
        elif current_state == ON:
            new_state = TURN_OFF if storage_tank > 60 or temperature_difference < 6 else STAY_ON

    elif operating_mode == FAIL:
        new_state = TURN_OFF

    ## Reset timer ##
            
    if current_state != new_state:
        last_change = ticks_ms()

    return new_state
