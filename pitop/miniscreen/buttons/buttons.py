from pitop.miniscreen import MiniscreenButton

from pitopcommon.ptdm import (
    PTDMSubscribeClient,
    Message
)
from pitopcommon.lock import PTLock
from pitopcommon.singleton import Singleton

from os import getenv
import atexit


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

    def __init__(self):
        self.up = MiniscreenButtonLegacy(self.UP)
        self.down = MiniscreenButtonLegacy(self.DOWN)
        self.select = MiniscreenButtonLegacy(self.SELECT)
        self.cancel = MiniscreenButtonLegacy(self.CANCEL)

        self.__ptdm_subscribe_client = None
        self.__setup_subscribe_client()

        atexit.register(self.__clean_up)

        self.lock = PTLock("pt-buttons")

        if getenv('PT_MINISCREEN_SYSTEM', "0") != "1":
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
