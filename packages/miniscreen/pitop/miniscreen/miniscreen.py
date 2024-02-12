import atexit
import logging
from os import environ
from time import sleep

from pitop.common.lock import PTLock
from pitop.common.ptdm import Message, PTDMSubscribeClient

from .oled import OLED
from .oled.core import MiniscreenLockFileMonitor


class Miniscreen(OLED):
    """Represents a pi-top [4]'s miniscreen display.

    Also owns the surrounding 4 buttons as properties
    (:class:`up_button`, :class:`down_button`, :class:`select_button`,
    :class:`cancel_button`). See
    :class:`pitop.miniscreen.miniscreen.MiniscreenButton` for how to use these
    buttons.
    """

    def __init__(self):
        self.lock = PTLock("miniscreen")

        # When running user or system miniscreen apps, wait until
        # lock is released to continue
        if self.lock.is_locked() is True:
            logging.info(
                "There's another miniscreen instance running; sleeping until it's released"
            )
            while self.lock.is_locked():
                sleep(1)

        self.lock_file_monitor = MiniscreenLockFileMonitor(self.lock.path)
        if environ.get("PT_MINISCREEN_SYSTEM", "") != "1":
            self.lock.acquire()

        super(Miniscreen, self).__init__()

        self._up_button = MiniscreenButton()
        self._down_button = MiniscreenButton()
        self._select_button = MiniscreenButton()
        self._cancel_button = MiniscreenButton()

        self.__ptdm_subscribe_client = None
        self.__setup_subscribe_client()

        atexit.register(self.__clean_up)

    def __setup_subscribe_client(self):
        def set_button_state(button, pressed):
            button.is_pressed = pressed
            self.__ptdm_subscribe_client.invoke_callback_func_if_exists(
                button.when_pressed if button.is_pressed else button.when_released
            )

        self.__ptdm_subscribe_client = PTDMSubscribeClient()
        self.__ptdm_subscribe_client.initialise(
            {
                Message.PUB_V3_BUTTON_UP_PRESSED: lambda: set_button_state(
                    self._up_button, pressed=True
                ),
                Message.PUB_V3_BUTTON_UP_RELEASED: lambda: set_button_state(
                    self._up_button, pressed=False
                ),
                Message.PUB_V3_BUTTON_DOWN_PRESSED: lambda: set_button_state(
                    self._down_button, pressed=True
                ),
                Message.PUB_V3_BUTTON_DOWN_RELEASED: lambda: set_button_state(
                    self._down_button, pressed=False
                ),
                Message.PUB_V3_BUTTON_SELECT_PRESSED: lambda: set_button_state(
                    self._select_button, pressed=True
                ),
                Message.PUB_V3_BUTTON_SELECT_RELEASED: lambda: set_button_state(
                    self._select_button, pressed=False
                ),
                Message.PUB_V3_BUTTON_CANCEL_PRESSED: lambda: set_button_state(
                    self._cancel_button, pressed=True
                ),
                Message.PUB_V3_BUTTON_CANCEL_RELEASED: lambda: set_button_state(
                    self._cancel_button, pressed=False
                ),
            }
        )
        self.__ptdm_subscribe_client.start_listening()

    def __clean_up(self):
        self.lock_file_monitor.stop()
        if self.lock.is_locked():
            self.lock.release()

        try:
            self.__ptdm_subscribe_client.stop_listening()
        except Exception:
            pass

    @property
    def is_active(self):
        """Determine if the current miniscreen instance is in control of the
        miniscreen hardware.

        :return: whether the miniscreen instance is in control of the
            miniscreen hardware.
        :rtype: bool
        """
        return self.lock.is_locked()

    @property
    def up_button(self):
        """Gets the up button of the pi-top [4] miniscreen.

        :return: A gpiozero-like button instance representing the up button of the pi-top [4] miniscreen.
        :rtype: :class:`pitop.miniscreen.miniscreen.MiniscreenButton`
        """
        return self._up_button

    @property
    def down_button(self):
        """Gets the down button of the pi-top [4] miniscreen.

        :return: A gpiozero-like button instance representing the down button of the pi-top [4] miniscreen.
        :rtype: :class:`pitop.miniscreen.miniscreen.MiniscreenButton`
        """
        return self._down_button

    @property
    def select_button(self):
        """Gets the select button of the pi-top [4] miniscreen.

        :return: A gpiozero-like button instance representing the select button of the pi-top [4] miniscreen.
        :rtype: :class:`pitop.miniscreen.miniscreen.MiniscreenButton`
        """
        return self._select_button

    @property
    def cancel_button(self):
        """Gets the cancel button of the pi-top [4] miniscreen.

        :return: A gpiozero-like button instance representing the cancel button of the pi-top [4] miniscreen.
        :rtype: :class:`pitop.miniscreen.miniscreen.MiniscreenButton`
        """
        return self._cancel_button

    @property
    def when_user_controlled(self):
        """Function to call when user takes control of the miniscreen.

        This is used by pt-miniscreen to update its 'user-controlled'
        application state.
        """
        return self.lock_file_monitor.when_user_starts_using_oled

    @when_user_controlled.setter
    def when_user_controlled(self, callback):
        """Setter for function to call when user takes control of the
        miniscreen.

        This is used by pt-miniscreen to update its 'user-controlled'
        application state.
        """
        if not callable(callback):
            raise ValueError("Callback must be callable")

        self.lock_file_monitor.when_user_starts_using_oled = callback
        # Lockfile thread needs to be restarted to get updated callback reference
        self.lock_file_monitor.start()

    @property
    def when_system_controlled(self):
        """Function to call when user gives back control of the miniscreen to
        the system.

        This is used by pt-miniscreen to update its 'user-controlled'
        application state.
        """
        return self.lock_file_monitor.when_user_stops_using_oled

    @when_system_controlled.setter
    def when_system_controlled(self, callback):
        """Setter for function to call when user gives back control of the
        miniscreen to the system.

        This is used by pt-miniscreen to update its 'user-controlled'
        application state.
        """
        if not callable(callback):
            raise ValueError("Callback must be callable")

        self.lock_file_monitor.when_user_stops_using_oled = callback
        # Lockfile thread needs to be restarted to get updated callback reference
        self.lock_file_monitor.start()

    @property
    def _when_user_starts_using_oled(self):
        """Deprecated function."""
        return self.when_user_controlled

    @_when_user_starts_using_oled.setter
    def _when_user_starts_using_oled(self, callback):
        """Deprecated function."""
        self.when_user_controlled = callback

    @property
    def _when_user_stops_using_oled(self):
        """Deprecated function."""
        return self.when_system_controlled

    @_when_user_stops_using_oled.setter
    def _when_user_stops_using_oled(self, callback):
        """Deprecated function."""
        self.when_system_controlled = callback


class MiniscreenButton:
    """Represents one of the 4 buttons around the miniscreen display on a pi-
    top [4].

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
        """Get or set the button state as a boolean value.

        :rtype: bool
        """
        return self._is_pressed

    @is_pressed.setter
    def is_pressed(self, value):
        self._is_pressed = value

    @property
    def when_pressed(self):
        """Get or set the 'when pressed' button state callback function. When
        set, this callback function will be invoked when this event happens.

        :type callback: Function
        :param callback: Callback function to run when a button is
            pressed.
        """
        return self._when_pressed

    @when_pressed.setter
    def when_pressed(self, callback):
        self._when_pressed = callback

    @property
    def when_released(self):
        """Get or set the 'when released' button state callback function. When
        set, this callback function will be invoked when this event happens.

        :type callback: Function
        :param callback: Callback function to run when a button is
            released.
        """
        return self._when_released

    @when_released.setter
    def when_released(self, callback):
        self._when_released = callback
