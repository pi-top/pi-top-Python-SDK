from pitopcommon.ptdm import (
    PTDMSubscribeClient,
    Message
)
from pitopcommon.lock import PTLock

import atexit
from uuid import uuid1


class CaseButton:
    def __init__(self, button_type):
        #: Returns a string representing which button it is.
        self.type = button_type
        self.is_pressed = False  #: Returns True is button is pressed.
        self.when_pressed = (
            None
        )  #: If a method is assigned to this data member it will be invoked when the button is pressed.
        self.when_released = (
            None
        )  #: If a method is assigned to this data member it will be invoked when the button is released.


class CaseButtons:
    """
    Instantiates a single instance for each of the four button types up, down,
    select and cancel.
    """
    UP = "UP"
    DOWN = "DOWN"
    SELECT = "SELECT"
    CANCEL = "CANCEL"

    def __init__(self):
        self.up = CaseButton(self.UP)
        self.down = CaseButton(self.DOWN)
        self.select = CaseButton(self.SELECT)
        self.cancel = CaseButton(self.CANCEL)

        self.__ptdm_subscribe_client = None
        self.__setup_subscribe_client()

        atexit.register(self.__clean_up)

        self.uuid = uuid1()

        self.lock = PTLock(f"pt-buttons-{str(self.uuid)}")
        self.lock.acquire()

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
        self.lock.release()
        try:
            self.__ptdm_subscribe_client.stop_listening()
        except Exception:
            pass


buttons = CaseButtons()


def UpButton():
    """
    :return: A button object for the up button.
    :rtype: CaseButton
    """
    return buttons.up


def DownButton():
    """
    :return: A button object for the down button.
    :rtype: CaseButton
    """
    return buttons.down


def SelectButton():
    """
    :return: A button object for the select button.
    :rtype: CaseButton
    """
    return buttons.select


def CancelButton():
    """
    :return: A button object for the cancel button.
    :rtype: CaseButton
    """
    return buttons.cancel
