import esp8266.wemos.d1mini.status_led as status_led
from machine import ADC, Pin
from machine import Timer
from micropython import schedule
from utime import sleep_ms
import config

class Temperature():
    def __init__(self, state):
        self.state = state
        self.adc = ADC(config.ADC)
        self.solar_pin = Pin(config.SOLAR_GPIO, mode=Pin.OUT)
        self.solar_pin.off()
        self.tank_pin = Pin(config.TANK_GPIO, mode=Pin.OUT)
        self.tank_pin.off()
        self.timer = Timer(-1)
        self.counter = 0
        self.solar_temp = [self.read_solar_temp()] * config.AVERAGE
        self.tank_temp = [self.read_tank_temp()] * config.AVERAGE
        self.update()

    def update(self):
        self.counter = (self.counter + 1) % config.AVERAGE
        self.solar_temp[self.counter] = self.read_solar_temp()
        self.tank_temp[self.counter] = self.read_tank_temp()
        if self.counter == 1:
            self.state.set(
                solar_temp = round(sum(self.solar_temp) / config.AVERAGE),
                tank_temp = round(sum(self.tank_temp) / config.AVERAGE),
            )

    def read_solar_temp(self):
        self.solar_pin.on()
        return config.solar_adc_to_temp(self.read_adc())

    def read_tank_temp(self):
        self.tank_pin.on()
        return config.tank_adc_to_temp(self.read_adc())

    def read_adc(self):
        status_led.invert()
        n = 5
        val = 0
        for i in range(n):
            sleep_ms(100)
            val += self.adc.read()
        self.solar_pin.off()
        self.tank_pin.off()
        status_led.invert()
        return val / n

    def start(self, state):
        self._sched = False
        self.timer.deinit()
        
        def _cb(_):
            self._sched = False
            self.update()

        def cb(_):
            if not self._sched:
                self._sched = True
                schedule(_cb, 0)
        
        self.timer.init(
            period=round(config.FREQ * 1000),
            callback=cb
        )

    def stop(self, state):
        self.timer.deinit()
