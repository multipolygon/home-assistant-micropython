def solar_collector(adc):
    return (adc - 282.77) / 5.355

def storage_tank(adc):
    return (adc - 285.54) / 5.269
