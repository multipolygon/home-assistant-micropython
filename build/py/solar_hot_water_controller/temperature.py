from lib.esp8266.wemos.d1mini import status_led
from machine import ADC, Pin
from machine import Timer
from micropython import schedule
from utime import sleep_ms
import config

class Temperature():
    def __init__(self, state):
        self.state = state
        self.adc = ADC(config.THERMISTOR_ADC)
        self.solar_probe_pin = Pin(config.SOLAR_PROBE_GPIO, mode=Pin.OUT)
        self.solar_probe_pin.off()
        self.tank_probe_pin = Pin(config.TANK_PROBE_GPIO, mode=Pin.OUT)
        self.tank_probe_pin.off()
        self.timer = Timer(-1)
        self.counter = 0
        self.solar_temperature = [self.read_solar_temperature()] * config.AVERAGE
        self.tank_temperature = [self.read_tank_temperature()] * config.AVERAGE
        self.update()
        self.poll()

    def update(self):
        self.counter = (self.counter + 1) % config.AVERAGE
        self.solar_temperature[self.counter] = self.read_solar_temperature()
        self.tank_temperature[self.counter] = self.read_tank_temperature()
        self.state.set(
            solar_temperature = round(sum(self.solar_temperature) / config.AVERAGE),
            tank_temperature = round(sum(self.tank_temperature) / config.AVERAGE),
        )

    def read_solar_temperature(self):
        self.solar_probe_pin.on()
        return config.solar_adc_to_temperature(self.read_adc())

    def read_tank_temperature(self):
        self.tank_probe_pin.on()
        return config.tank_adc_to_temperature(self.read_adc())

    def read_adc(self):
        status_led.invert()
        val = 0
        for i in range(10):
            sleep_ms(100)
            val += self.adc.read()
        self.solar_probe_pin.off()
        self.tank_probe_pin.off()
        status_led.invert()
        return val / 10

    def poll(self):
        self.update_scheduled = False
        self.timer.deinit()
        
        def update(_):
            self.update_scheduled = False
            self.update()

        def schedule_update(_):
            if not self.update_scheduled:
                self.update_scheduled = True
                schedule(update, None)
        
        self.timer.init(period=config.UPDATE_INTERVAL * 1000, callback=schedule_update)

    def deinit(self):
        self.timer.deinit()
