from pitop.miniscreen.buttons import UpButton
from unittest.mock import MagicMock
from unittest import TestCase, main
import sys

sys.modules["request_client"] = MagicMock()
sys.modules["threading"] = MagicMock()
sys.modules["zmq"] = MagicMock()
sys.modules["pitop.utils"] = MagicMock()
sys.modules["pitop.utils.logger"] = MagicMock()
sys.modules["pitop.utils.ptdm_message"] = MagicMock()


class PTButtonsCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_when_pressed(self):
        def a():
            pass

        test_up_button = UpButton()
        test_up_button.when_pressed = MagicMock(side_effect=a)
        test_up_button.when_pressed.assert_not_called()
        test_up_button.when_pressed()
        test_up_button.when_pressed.assert_called()


if __name__ == "__main__":
    main()
