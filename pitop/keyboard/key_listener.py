from pynput.keyboard import Listener


class KeyPressListener:
    def __init__(self, key):
        """
        This class is designed to simulate a button press similar to the button in the gpiozero,
         but with a key press from your keyboard.
        """
        self.key = key
        self.pressed_method = None
        self.released_method = None
        self._key_pressed = False
        self.listener = Listener(
            on_press=self._on_press, on_release=self._on_release)
        self.listener.start()

    def _on_press(self, key):
        received_key = None
        try:
            received_key = key.char
        except AttributeError:
            received_key = key
        received_key = str(received_key)
        if "Key." in received_key:
            received_key = received_key.replace("Key.", "")
        if received_key == self.key:
            self._key_pressed = True
            if self.pressed_method is not None:
                self.pressed_method()

    def _on_release(self, key):
        self._key_pressed = False
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
        Set a callback method to be called when the key is pressed.

        :param method callback: A method to be called when the button is pressed
        """

    @when_pressed.setter
    def when_pressed(self, method=None):
        if method is None:
            raise "Error: no method assigned"
        self.pressed_method = method

    @property
    def when_released(self):
        """
        Set a callback method to be called when the key is released.

        :param method callback: A method to be called when the button is released
        """

    @when_released.setter
    def when_released(self, method=None):
        if method is None:
            raise "Error: no method assigned"
        self.released_method = method

    @property
    def is_pressed(self) -> bool:
        """
        Determine whether the key is pressed.

        :return: True if the key is pressed, False otherwise
        :rtype: bool
        """
        if self._key_pressed is True:
            return True
        else:
            return False
