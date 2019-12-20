from lib.esp8266.wemos.d1mini.oled import OLED
import framebuf
import utime

class OLEDBigText(OLED):
    def bigchar(self, char):
        if self.display:            
            self.display.fill(0)
            if self.charbuffer == None:
                self.charbuffer = framebuf.FrameBuffer1(memoryview(bytearray(8)), 8, 8)
            self.charbuffer.fill(0)
            self.charbuffer.text(char, 0, 0, 1)
            for x in range(0,8):
                for y in range(0,8):
                    self.display.fill_rect(8 + x * 6, y * 6, 6, 6, self.charbuffer.pixel(x,y))
            self.display.show()

    def timestamp(self):
        if self.display:
            localtime = utime.localtime(utime.time() + self.utc_offset * 60 * 60)
            w, h, lh = self.width, self.height, self.line_height
            bw, bh = 42, 9
            self.display.fill_rect(w - bw - 1, 0, bw + 1, bh + 1, 0)
            self.display.fill_rect(w - bw, 0, bw, bh, 1)
            self.display.text("%2d:%02d" % (localtime[3], localtime[4]), w - bw + 1, 1, 0)
            self.display.show()
