from utime import ticks_ms, ticks_diff

MAX_DUTY_CYCLE = 5 # minutes
FAILURE_DELAY = 60 # minutes

last_change = ticks_ms()
timer = 0
normal_operation = True

def logic(solar_collector, storage_tank, current_state):
    global last_change
    global timer
    global normal_operation

    timer = ticks_diff(ticks_ms(), last_change) / 1000 / 60 # minutes

    normal_operation = (
        current_state == False or timer < MAX_DUTY_CYCLE
    ) if normal_operation else (
        timer > FAILURE_DELAY
    )

    new_state = (
        # Pump is already running:
        normal_operation and
        storage_tank < 60 and
        solar_collector - storage_tank > 6
    ) if current_state else (
        # Pump is currently off:
        normal_operation and
        storage_tank < 60 and
        solar_collector - storage_tank > 12
    )
    
    if current_state != new_state:
        last_change = ticks_ms()

    return new_state
