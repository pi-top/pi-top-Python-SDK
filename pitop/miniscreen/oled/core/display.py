class Display:
    def __init__(self, oled_device):
        self._visible = False
        self.__oled_device = oled_device

    def reset(self):
        """
        Resets the display
        """
        self.__oled_device.contrast(255)
        self.show()

    def hide(self):
        """
        The pi-top OLED display is put into low power mode. The previously
        shown image will re-appear when show() is given, even if the
        internal frame buffer has been changed (so long as draw() has not
        been called).
        """
        self.__oled_device.hide()
        self._visible = False

    def show(self):
        """
        The pi-top OLED display comes out of low power mode showing the
        previous image shown before hide() was called (so long as draw()
        has not been called)
        """
        self.__oled_device.show()
        self._visible = True

    def is_hidden(self):
        """
        Returns whether the device is currently in low power state
        :return: whether the the screen is in low power mode
        :rtype: bool
        """
        return self._visible
