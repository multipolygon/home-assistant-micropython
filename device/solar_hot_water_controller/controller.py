from utime import ticks_ms, ticks_diff

DUTY_CYCLE = 5 # minutes
REST_CYCLE = 5 # minutes

last_change = None
timer = None

def logic(solar_collector, storage_tank, current_state):
    global last_change
    global timer
    
    timer = REST_CYCLE if last_change == None else ticks_diff(ticks_ms(), last_change) / 1000 / 60 # minutes

    new_state = (
        # Pump is already running:
        storage_tank < 60 and
        solar_collector - storage_tank > 6 and
        timer < DUTY_CYCLE
    ) if current_state else (
        # Pump is currently off:
        storage_tank < 60 and
        solar_collector - storage_tank > 12 and
        timer >= REST_CYCLE
    )
    
    if current_state != new_state:
        last_change = ticks_ms()

    return new_state
