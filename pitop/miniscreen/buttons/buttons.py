from pitopcommon.ptdm import (
    PTDMSubscribeClient,
    Message
)
from pitopcommon.lock import PTLock
from pitopcommon.singleton import Singleton

import atexit


class Button:
    def __init__(self, button_type):
        # State parameters
        self.type = button_type
        self.is_pressed = False
        # Event-based functions
        self.when_pressed = None
        self.when_released = None


class Buttons(metaclass=Singleton):
    """
    Instantiates a single instance for each of the four button types up, down,
    select and cancel.
    """
    UP = "UP"
    DOWN = "DOWN"
    SELECT = "SELECT"
    CANCEL = "CANCEL"

    def __init__(self, _exclusive_mode=True):
        self.up = Button(self.UP)
        self.down = Button(self.DOWN)
        self.select = Button(self.SELECT)
        self.cancel = Button(self.CANCEL)

        self.__exclusive_mode = _exclusive_mode

        self.__ptdm_subscribe_client = None
        self.__setup_subscribe_client()

        atexit.register(self.__clean_up)

        self.lock = PTLock("pt-buttons")
        if self.__exclusive_mode:
            self.lock.acquire()

    @property
    def is_active(self):
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


def UpButton():
    """
    :return: A button object for the up button.
    :rtype: Button
    """
    return Buttons().up


def DownButton():
    """
    :return: A button object for the down button.
    :rtype: Button
    """
    return Buttons().down


def SelectButton():
    """
    :return: A button object for the select button.
    :rtype: Button
    """
    return Buttons().select


def CancelButton():
    """
    :return: A button object for the cancel button.
    :rtype: Button
    """
    return Buttons().cancel
