from pitop.miniscreen.oled.core.contrib.luma.core.device import device
import pitop.miniscreen.oled.core.contrib.luma.core.error
import pitop.miniscreen.oled.core.contrib.luma.oled.const


class sh1106(device):
    """Serial interface to a monochrome SH1106 OLED display.

    On creation, an initialization sequence is pumped to the display to
    properly configure it. Further control commands can then be called
    to affect the brightness and other settings.
    """

    def __init__(self, serial_interface=None, width=128, height=64, rotate=0, **kwargs):
        super(sh1106, self).__init__(pitop.miniscreen.oled.core.contrib.luma.oled.const.sh1106, serial_interface)
        self.capabilities(width, height, rotate)
        self._pages = self._h // 8

        settings = {
            (128, 128): dict(multiplex=0xFF, displayoffset=0x02),
            (128, 64): dict(multiplex=0x3F, displayoffset=0x00),
            (128, 32): dict(multiplex=0x20, displayoffset=0x0F)
        }.get((width, height))

        if settings is None:
            raise pitop.miniscreen.oled.core.contrib.luma.core.error.DeviceDisplayModeError(
                f"Unsupported display mode: {width} x {height}")

        self.command(
            self._const.DISPLAYOFF,
            self._const.MEMORYMODE,
            self._const.SETHIGHCOLUMN,      0xB0, 0xC8,
            self._const.SETLOWCOLUMN,       0x10, 0x40,
            self._const.SETSEGMENTREMAP,
            self._const.NORMALDISPLAY,
            self._const.SETMULTIPLEX,       settings['multiplex'],
            self._const.DISPLAYALLON_RESUME,
            self._const.SETDISPLAYOFFSET,   settings['displayoffset'],
            self._const.SETDISPLAYCLOCKDIV, 0xF0,
            self._const.SETPRECHARGE,       0x22,
            self._const.SETCOMPINS,         0x12,
            self._const.SETVCOMDETECT,      0x20,
            self._const.CHARGEPUMP,         0x14)

        self.contrast(0x7F)
        self.clear()
        self.show()

    def display(self, image):
        """Takes a 1-bit :py:mod:`PIL.Image` and dumps it to the SH1106 OLED
        display.

        :param image: Image to display.
        :type image: :py:mod:`PIL.Image`
        """
        assert(image.mode == self.mode)
        assert(image.size == self.size)

        image = self.preprocess(image)

        set_page_address = 0xB0
        image_data = image.getdata()
        pixels_per_page = self.width * 8
        buf = bytearray(self.width)

        for y in range(0, int(self._pages * pixels_per_page), pixels_per_page):
            self.command(set_page_address, 0x02, 0x10)
            set_page_address += 1
            offsets = [y + self.width * i for i in range(8)]

            for x in range(self.width):
                buf[x] = \
                    (image_data[x + offsets[0]] and 0x01) | \
                    (image_data[x + offsets[1]] and 0x02) | \
                    (image_data[x + offsets[2]] and 0x04) | \
                    (image_data[x + offsets[3]] and 0x08) | \
                    (image_data[x + offsets[4]] and 0x10) | \
                    (image_data[x + offsets[5]] and 0x20) | \
                    (image_data[x + offsets[6]] and 0x40) | \
                    (image_data[x + offsets[7]] and 0x80)

            self.data(list(buf))
