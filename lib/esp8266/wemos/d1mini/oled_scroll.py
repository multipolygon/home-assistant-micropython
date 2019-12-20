from lib.esp8266.wemos.d1mini.oled import OLED

class OLEDScroll(OLED):
    def write(self, line, show=True):
        if self.display:
            w, h, lh = self.width, self.height, self.line_height
            self.display.scroll(0, -1 * lh)
            self.display.fill_rect(0, h - lh, w, lh, 0)
            self.display.text(line[0:w//8], 0, h - lh)
            if show:
                self.display.show()
        return line
