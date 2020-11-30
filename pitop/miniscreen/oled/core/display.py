from pitop.miniscreen.oled.oled_controls import get_oled_device


class Display:
    def __init__(self):
        self._visible = False

    def reset(self):
        """
        Resets the display
        """
        get_oled_device().contrast(255)
        self.show()

    def hide(self):
        """
        The pi-top OLED display is put into low power mode. The previously
        shown image will re-appear when show() is given, even if the
        internal frame buffer has been changed (so long as draw() has not
        been called).
        """
        get_oled_device().hide()
        self._visible = False

    def show(self):
        """
        The pi-top OLED display comes out of low power mode showing the
        previous image shown before hide() was called (so long as draw()
        has not been called)
        """
        get_oled_device().show()
        self._visible = True

    def is_hidden(self):
        """
        Returns whether the device is currently in low power state
        :return: whether the the screen is in low power mode
        :rtype: bool
        """
        return self._visible
