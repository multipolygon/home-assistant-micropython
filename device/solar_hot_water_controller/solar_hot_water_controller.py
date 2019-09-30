def logic(solar_collector, storage_tank, water_pump):
    if solar_collector > 98:
        ## Too hot, don't want water to vaporise
        water_pump.off()

    elif storage_tank > 60:
        ## Water is hot enough
        water_pump.off()

    else:
        if water_pump.value():
            ## Pump is on
            if solar_collector - storage_tank < 6:
                ## Stop heating
                water_pump.off()

        else:
            ## Pump is off
            if solar_collector - storage_tank > 12:
                ## Start heating
                water_pump.on()
