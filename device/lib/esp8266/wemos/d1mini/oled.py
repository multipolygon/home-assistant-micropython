from machine import I2C, Pin
import utime
import framebuf
from ssd1306 import SSD1306_I2C

import pinmap

error = False

w = 64
h = 48
lh = h // 4 # line height

local_offset = 10 ## TODO

i2c = I2C(-1, Pin(pinmap.SCL), Pin(pinmap.SDA))

try:
    display = SSD1306_I2C(w, h, i2c)
    display.poweron()
    display.contrast(255)
    display.fill(0)
    display.text('POWER ON', 0, 0)
    display.show()
except:
    display = None
    error = True

charbuffer = framebuf.FrameBuffer1(memoryview(bytearray(8)), 8, 8)

def isavailable():
    return not error

def clear():
    display.fill(0)
    display.show()

def write(line, show=True):
    print(line)
    if not error:
        display.scroll(0, -1 * lh)
        display.fill_rect(0, h - lh, w, lh, 0)
        display.text(line[0:w//8], 0, h - lh)
        if show:
            display.show()

def bigchar(char):
    print(char)
    if not error:
        display.fill(0)
        charbuffer.fill(0)
        charbuffer.text(char, 0, 0, 1)
        for x in range(0,8):
            for y in range(0,8):
                display.fill_rect(8 + x * 6, y * 6, 6, 6, charbuffer.pixel(x,y))
        display.show()

def timestamp():
    localtime = utime.localtime(utime.time() + local_offset * 60 * 60)
    bw, bh = 42, 9
    display.fill_rect(w - bw - 1, 0, bw + 1, bh + 1, 0)
    display.fill_rect(w - bw, 0, bw, bh, 1)
    display.text("%2d:%02d" % (localtime[3], localtime[4]), w - bw + 1, 1, 0)
    display.show()

def poweroff():
    if not error:
        display.poweroff()

