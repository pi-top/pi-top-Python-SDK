from ptbuttons import PTUpButton, PTDownButton, PTSelectButton, PTCancelButton
from unittest.mock import MagicMock, patch
from unittest import TestCase, main
import sys

sys.modules["request_client"] = MagicMock()
sys.modules["threading"] = MagicMock()
sys.modules["zmq"] = MagicMock()
sys.modules["ptcommon"] = MagicMock()
sys.modules["ptcommon.logger"] = MagicMock()
sys.modules["ptcommon.ptdm_message"] = MagicMock()


class PTButtonsCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_when_pressed(self):
        def a():
            pass

        test_up_button = PTUpButton()
        test_up_button.when_pressed = MagicMock(side_effect=a)
        test_up_button.when_pressed.assert_not_called()
        test_up_button.when_pressed()
        test_up_button.when_pressed.assert_called()


if __name__ == "__main__":
    main()
