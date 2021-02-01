from pitopcommon.ptdm import (
    PTDMSubscribeClient,
    Message
)
from pitopcommon.lock import PTLock
from pitopcommon.singleton import Singleton

import atexit


class MiniscreenButton:
    """
    Represents one of the 4 buttons around the miniscreen display on a pi-top [4].
    Should not be created directly - instead, use :class:`pitop.miniscreen.Miniscreen`.
    """

    def __init__(self):
        # State parameters
        self._is_pressed = False
        # Event-based functions
        self._when_pressed = None
        self._when_released = None

    @property
    def is_pressed(self):
        """
        Get or set the button state as a boolean value.

        :rtype: bool
        """
        return self._is_pressed

    @is_pressed.setter
    def is_pressed(self, value):
        self._is_pressed = value

    @property
    def when_pressed(self):
        """
        Get or set the 'when pressed' button state callback function.
        When set, this callback function will be invoked when this event happens.

        :type callback: Function
        :param callback:
            Callback function to run when a button is pressed.
        """
        return self._when_pressed

    @when_pressed.setter
    def when_pressed(self, callback):
        self._when_pressed = callback

    @property
    def when_released(self):
        """
        Get or set the 'when released' button state callback function.
        When set, this callback function will be invoked when this event happens.

        :type callback: Function
        :param callback:
            Callback function to run when a button is released.
        """
        return self._when_released

    @when_released.setter
    def when_released(self, callback):
        self._when_released = callback


class MiniscreenButtonLegacy(MiniscreenButton):
    def __init__(self, button_type):
        super(MiniscreenButtonLegacy, self).__init__()

        # State parameters
        self.type = button_type


class Buttons(metaclass=Singleton):
    """
    Instantiates a button for each one of the four types (up, down,
    select and cancel), configuring them to receive event press events
    from the device manager.
    """
    UP = "UP"
    DOWN = "DOWN"
    SELECT = "SELECT"
    CANCEL = "CANCEL"

    def __init__(self, _exclusive_mode=True):
        self.up = MiniscreenButtonLegacy(self.UP)
        self.down = MiniscreenButtonLegacy(self.DOWN)
        self.select = MiniscreenButtonLegacy(self.SELECT)
        self.cancel = MiniscreenButtonLegacy(self.CANCEL)

        self.__exclusive_mode = _exclusive_mode

        self.__ptdm_subscribe_client = None
        self.__setup_subscribe_client()

        atexit.register(self.__clean_up)

        self.lock = PTLock("pt-buttons")
        if self.__exclusive_mode:
            self.lock.acquire()

    @property
    def is_active(self):
        """
        Determine if the current instance is in control of the buttons.

        :rtype: bool
        """
        return self.lock.is_locked()

    def __setup_subscribe_client(self):
        def set_button_state(button, pressed):
            button.is_pressed = pressed
            self.__ptdm_subscribe_client.invoke_callback_func_if_exists(
                button.when_pressed if button.is_pressed else button.when_released
            )

        self.__ptdm_subscribe_client = PTDMSubscribeClient()
        self.__ptdm_subscribe_client.initialise(
            {
                Message.PUB_V3_BUTTON_UP_PRESSED: lambda: set_button_state(self.up, pressed=True),
                Message.PUB_V3_BUTTON_UP_RELEASED: lambda: set_button_state(self.up, pressed=False),
                # ----------------------------------------------------------------------------------
                Message.PUB_V3_BUTTON_DOWN_PRESSED: lambda: set_button_state(self.down, pressed=True),
                Message.PUB_V3_BUTTON_DOWN_RELEASED: lambda: set_button_state(self.down, pressed=False),
                # ----------------------------------------------------------------------------------
                Message.PUB_V3_BUTTON_SELECT_PRESSED: lambda: set_button_state(self.select, pressed=True),
                Message.PUB_V3_BUTTON_SELECT_RELEASED: lambda: set_button_state(self.select, pressed=False),
                # ----------------------------------------------------------------------------------
                Message.PUB_V3_BUTTON_CANCEL_PRESSED: lambda: set_button_state(self.cancel, pressed=True),
                Message.PUB_V3_BUTTON_CANCEL_RELEASED: lambda: set_button_state(self.cancel, pressed=False),
            }
        )
        self.__ptdm_subscribe_client.start_listening()

    def __clean_up_lock(self):
        if self.is_active:
            self.lock.release()

    def __clean_up(self):
        self.__clean_up_lock()

        try:
            self.__ptdm_subscribe_client.stop_listening()
        except Exception:
            pass


class UpButton(MiniscreenButton):
    """
    pi-top [4] Miniscreen 'Up' button.
    """

    def __init__(self):
        pass

    def __new__(cls):
        return Buttons().up


class DownButton(MiniscreenButton):
    """
    pi-top [4] Miniscreen 'Down' button.
    """

    def __init__(self):
        pass

    def __new__(cls):
        return Buttons().down


class SelectButton(MiniscreenButton):
    """
    pi-top [4] Miniscreen 'Select' button.
    """

    def __init__(self):
        pass

    def __new__(cls):
        return Buttons().select


class CancelButton(MiniscreenButton):
    """
    pi-top [4] Miniscreen 'Cancel' button.
    """

    def __init__(self):
        pass

    def __new__(cls):
        return Buttons().cancel
