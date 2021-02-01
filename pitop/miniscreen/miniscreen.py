from .oled import OLED
from .buttons import (
    UpButton,
    DownButton,
    SelectButton,
    CancelButton
)


class Miniscreen(OLED):
    def __init__(self, _exclusive_mode=True):
        super(Miniscreen, self).__init__(_exclusive_mode)

        self._up_button = UpButton()
        self._down_button = DownButton()
        self._select_button = SelectButton()
        self._cancel_button = CancelButton()

    @property
    def up_button(self):
        """
        Gets the up button of the pi-top [4] miniscreen.

        :return: A gpiozero-like button instance representing the up button of the pi-top [4] miniscreen.
        :rtype: :class:`UpButton`
        """
        return self._up_button

    @property
    def down_button(self):
        """
        Gets the down button of the pi-top [4] miniscreen.

        :return: A gpiozero-like button instance representing the down button of the pi-top [4] miniscreen.
        :rtype: :class:`DownButton`
        """
        return self._down_button

    @property
    def select_button(self):
        """
        Gets the select button of the pi-top [4] miniscreen.

        :return: A gpiozero-like button instance representing the select button of the pi-top [4] miniscreen.
        :rtype: :class:`SelectButton`
        """
        return self._select_button

    @property
    def cancel_button(self):
        """
        Gets the cancel button of the pi-top [4] miniscreen.

        :return: A gpiozero-like button instance representing the cancel button of the pi-top [4] miniscreen.
        :rtype: :class:`CancelButton`
        """
        return self._cancel_button
