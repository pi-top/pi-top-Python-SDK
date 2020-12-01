from pitopcommon.ptdm import PTDMSubscribeClient, Message

import atexit
from os import path, mkdir, getpid, chmod, remove
from fcntl import flock, LOCK_UN, LOCK_EX


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

    __ptdm_subscribe_client = None
    UP = "UP"
    DOWN = "DOWN"
    SELECT = "SELECT"
    CANCEL = "CANCEL"

    def __init__(self):
        self.up = CaseButton(self.UP)
        self.down = CaseButton(self.DOWN)
        self.select = CaseButton(self.SELECT)
        self.cancel = CaseButton(self.CANCEL)
        self._setup_subscribe_client()
        atexit.register(self._clean_up)
        if path.exists("/tmp/button-locks") is False:
            mkdir("/tmp/button-locks")
        self.lock_path = "/tmp/button-locks/pt-buttons-" + \
            str(getpid()) + ".lock"
        self.lock_handle = open(self.lock_path, "w")
        self._acquire_buttons_lock()

    def _setup_subscribe_client(self):
        def get_message_dict():
            def __invoke_method_if_exists(method):
                if method is not None:
                    method()

            def set_up_button_pressed():
                self.up.is_pressed = True
                __invoke_method_if_exists(self.up.when_pressed)

            def set_down_button_pressed():
                self.down.is_pressed = True
                __invoke_method_if_exists(self.down.when_pressed)

            def set_select_button_pressed():
                self.select.is_pressed = True
                __invoke_method_if_exists(self.select.when_pressed)

            def set_cancel_button_pressed():
                self.cancel.is_pressed = True
                __invoke_method_if_exists(self.cancel.when_pressed)

            def set_up_button_released():
                self.up.is_pressed = False
                __invoke_method_if_exists(self.up.when_released)

            def set_down_button_released():
                self.down.is_pressed = False
                __invoke_method_if_exists(self.down.when_released)

            def set_select_button_released():
                self.select.is_pressed = False
                __invoke_method_if_exists(self.select.when_released)

            def set_cancel_button_released():
                self.cancel.is_pressed = False
                __invoke_method_if_exists(self.cancel.when_released)

            message_dict = {}
            message_dict[Message.PUB_V3_BUTTON_UP_PRESSED] = set_up_button_pressed()
            message_dict[Message.PUB_V3_BUTTON_DOWN_PRESSED] = set_down_button_pressed()
            message_dict[Message.PUB_V3_BUTTON_SELECT_PRESSED] = set_select_button_pressed()
            message_dict[Message.PUB_V3_BUTTON_CANCEL_PRESSED] = set_cancel_button_pressed()
            message_dict[Message.PUB_V3_BUTTON_UP_RELEASED] = set_up_button_released()
            message_dict[Message.PUB_V3_BUTTON_DOWN_RELEASED] = set_down_button_released()
            message_dict[Message.PUB_V3_BUTTON_SELECT_RELEASED] = set_select_button_released()
            message_dict[Message.PUB_V3_BUTTON_CANCEL_RELEASED] = set_cancel_button_released()

            return message_dict
        self.__ptdm_subscribe_client = PTDMSubscribeClient()
        self.__ptdm_subscribe_client.initialise(get_message_dict())
        self.__ptdm_subscribe_client.start_listening()

    def _clean_up(self):
        self._release_buttons_lock()
        try:
            self.__ptdm_subscribe_client.stop_listening()
        except Exception:
            pass

    def _acquire_buttons_lock(self):
        try:
            chmod(self.lock_path, 0o777)
            flock(self.lock_handle, LOCK_EX)
        except IOError as error:
            print(error)
        except Exception:
            pass

    def _release_buttons_lock(self):
        if self.lock_handle is not None:
            flock(self.lock_handle.fileno(), LOCK_UN)
            self.lock_handle.close()
            remove(self.lock_path)


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
