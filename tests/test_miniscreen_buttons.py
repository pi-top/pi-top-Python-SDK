from sys import modules
from unittest.mock import MagicMock

modules["request_client"] = MagicMock()
modules["threading"] = MagicMock()
modules["pyinotify"] = MagicMock()
modules["pitopcommon.lock"] = MagicMock()
modules["pitopcommon.logger"] = MagicMock()
modules["pitopcommon.ptdm"] = MagicMock()
modules["RPi"] = MagicMock()
modules["RPi.GPIO"] = MagicMock()
modules["luma.core.interface.serial"] = MagicMock()
modules["luma.oled.device"] = MagicMock()

from unittest import TestCase, main
from pitop import Miniscreen


class PTButtonsCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_when_pressed(self):
        def a():
            pass

        test_up_button = Miniscreen().up_button
        test_up_button.when_pressed = MagicMock(side_effect=a)
        test_up_button.when_pressed.assert_not_called()
        test_up_button.when_pressed()
        test_up_button.when_pressed.assert_called()


if __name__ == "__main__":
    main()
