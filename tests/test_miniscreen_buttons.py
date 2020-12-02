from unittest.mock import MagicMock
from unittest import TestCase, main
from sys import modules

modules["request_client"] = MagicMock()
modules["threading"] = MagicMock()
modules["zmq"] = MagicMock()
modules["pitopcommon.lock"] = MagicMock()
modules["pitopcommon.logger"] = MagicMock()
modules["pitopcommon.ptdm"] = MagicMock()

# import after applying mocks
from pitop.miniscreen.buttons import UpButton  # noqa: E402


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
