from pitopcommon.current_session_info import get_first_display
from os import environ


class KeyboardButton:
    def __init__(self, key):
        """
        This class is designed to simulate a button press similar to the button in the gpiozero,
         but with a key press from your keyboard.
        """
        self.key = key
        self.pressed_method = None
        self.released_method = None
        self.__key_pressed = False

        if not environ.get("DISPLAY"):
            environ["DISPLAY"] = str(get_first_display())

        from pynput.keyboard import Listener

        self.listener = Listener(
            on_press=self.__on_press, on_release=self.__on_release)
        self.listener.start()

    def __on_press(self, key):
        received_key = None
        try:
            received_key = key.char
        except AttributeError:
            received_key = key
        received_key = str(received_key)
        if "Key." in received_key:
            received_key = received_key.replace("Key.", "")
        if received_key == self.key:
            self.__key_pressed = True
            if self.pressed_method is not None:
                self.pressed_method()

    def __on_release(self, key):
        self.__key_pressed = False
        received_key = None
        try:
            received_key = key.char
        except AttributeError:
            received_key = key
        received_key = str(received_key)
        if "Key." in received_key:
            received_key = received_key.replace("Key.", "")
        if received_key == self.key:
            if self.released_method is not None:
                self.released_method()

    @property
    def when_pressed(self):
        """
        Get or set the 'when pressed' button state callback function.
        When set, this callback function will be invoked when this event happens.

        :type callback: Function
        :param callback:
            Callback function to run when a button is pressed.
        """

    @when_pressed.setter
    def when_pressed(self, method=None):
        if method is None:
            raise "Error: no method assigned"
        self.pressed_method = method

    @property
    def when_released(self):
        """
        Get or set the 'when released' button state callback function.
        When set, this callback function will be invoked when this event happens.

        :type callback: Function
        :param callback:
            Callback function to run when a button is released.
        """

    @when_released.setter
    def when_released(self, method=None):
        if method is None:
            raise "Error: no method assigned"
        self.released_method = method

    @property
    def is_pressed(self) -> bool:
        """
        Get or set the button state as a boolean value.

        :rtype: bool
        """
        if self.__key_pressed is True:
            return True
        else:
            return False
