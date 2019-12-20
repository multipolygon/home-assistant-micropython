from lib.esp8266.wemos.d1mini import pinmap
from machine import I2C, Pin
from ssd1306 import SSD1306_I2C

class OLED():
    def __init__(self):
        self.width = w = 64
        self.height = h = 48
        self.line_height = lh = h // 4

        try:
            i2c = I2C(-1, Pin(pinmap.SCL), Pin(pinmap.SDA))
            self.display = display = SSD1306_I2C(w, h, i2c)
            display.poweron()
            display.contrast(255)
            display.fill(0)
            display.show()
        except:
            self.display = None

    def is_available(self):
        return self.display != None

    def clear(self):
        if self.display:
            self.display.fill(0)
            self.display.show()

    def write_lines(self, *lines):
        if self.display:
            self.display.fill(0)
            w, h, lh = self.width, self.height, self.line_height
            for row, line in enumerate(lines[0:4]):
                self.display.text(line[0:w//8], 0, lh * row)
            self.display.show()

    def power_off(self):
        if self.display:
            self.display.poweroff()
