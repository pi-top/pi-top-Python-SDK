from pitopcommon.ptdm import (
    PTDMSubscribeClient,
    Message
)
from pitopcommon.lock import PTLock

import atexit
from uuid import uuid1


class Button:
    def __init__(self, button_type):
        # State parameters
        self.type = button_type
        self.is_pressed = False
        # Event-based functions
        self.when_pressed = None
        self.when_released = None


class Buttons:
    """
    Instantiates a single instance for each of the four button types up, down,
    select and cancel.
    """
    UP = "UP"
    DOWN = "DOWN"
    SELECT = "SELECT"
    CANCEL = "CANCEL"

    def __init__(self):
        self.up = Button(self.UP)
        self.down = Button(self.DOWN)
        self.select = Button(self.SELECT)
        self.cancel = Button(self.CANCEL)

        self.__ptdm_subscribe_client = None
        self.__setup_subscribe_client()

        atexit.register(self.__clean_up)

        self.uuid = uuid1()

        self.exclusive_mode = False
        self.lock = None
        self.__configure_locks()

    def _set_exclusive_mode(self, exclusive):
        self.exclusive_mode = exclusive
        self.__configure_locks()

    def __configure_locks(self):
        if self.exclusive_mode:
            # UUID makes this lock single-purpose
            #
            # This is actually just a hack workaround to let pt-sys-oled know that
            # the buttons are in use. In an ideal world, there would be a way
            # to ask pt-device-manager how many things are registered to listen
            # for particular events
            self.lock = PTLock(f"pt-buttons-{str(self.uuid)}", _single_purpose=True)
            self.lock.acquire()
        else:
            if self.lock is not None:
                self.lock.release()
                self.lock = None

    def __setup_subscribe_client(self):
        def set_button_state(button, pressed_state):
            button.is_pressed = pressed_state
            self.__ptdm_subscribe_client.invoke_callback_func_if_exists(
                button.when_pressed if button.is_pressed else button.when_released
            )

        self.__ptdm_subscribe_client = PTDMSubscribeClient()
        self.__ptdm_subscribe_client.initialise(
            {
                Message.PUB_V3_BUTTON_UP_PRESSED: lambda: set_button_state(self.up, True),
                Message.PUB_V3_BUTTON_UP_RELEASED: lambda: set_button_state(self.up, False),
                # ----------------------------------------------------------------------------------
                Message.PUB_V3_BUTTON_DOWN_PRESSED: lambda: set_button_state(self.down, True),
                Message.PUB_V3_BUTTON_DOWN_RELEASED: lambda: set_button_state(self.down, False),
                # ----------------------------------------------------------------------------------
                Message.PUB_V3_BUTTON_SELECT_PRESSED: lambda: set_button_state(self.select, True),
                Message.PUB_V3_BUTTON_SELECT_RELEASED: lambda: set_button_state(self.select, False),
                # ----------------------------------------------------------------------------------
                Message.PUB_V3_BUTTON_CANCEL_PRESSED: lambda: set_button_state(self.cancel, True),
                Message.PUB_V3_BUTTON_CANCEL_RELEASED: lambda: set_button_state(self.cancel, False),
            }
        )
        self.__ptdm_subscribe_client.start_listening()

    def __clean_up(self):
        if self.lock is not None:
            self.lock.release()

        try:
            self.__ptdm_subscribe_client.stop_listening()
        except Exception:
            pass


buttons = Buttons()


def UpButton():
    """
    :return: A button object for the up button.
    :rtype: Button
    """
    return buttons.up


def DownButton():
    """
    :return: A button object for the down button.
    :rtype: Button
    """
    return buttons.down


def SelectButton():
    """
    :return: A button object for the select button.
    :rtype: Button
    """
    return buttons.select


def CancelButton():
    """
    :return: A button object for the cancel button.
    :rtype: Button
    """
    return buttons.cancel
