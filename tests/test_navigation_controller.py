from sys import modules
from unittest.mock import Mock, patch
from unittest import TestCase

modules_to_patch = [
    "pitop.camera.camera",
    "atexit",
    "numpy",
    "simple_pid",
    "pitopcommon.common_ids",
    "pitopcommon.current_session_info",
    "pitopcommon.ptdm",
    "pitopcommon.firmware_device",
    "pitopcommon.command_runner",
    "pitopcommon.common_names",
    "pitopcommon.smbus_device",
    "pitopcommon.logger",
    "pitopcommon.singleton",
]
for module in modules_to_patch:
    modules[module] = Mock()

from pitop.pma.encoder_motor import EncoderMotor
from pitop.pma.parameters import (
    BrakingType,
    ForwardDirection,
    Direction
)

# Avoid getting the mocked modules in other tests
for patched_module in modules_to_patch:
    del modules[patched_module]


class TestNavigationController(TestCase):

    def setUp(self):
        pass

    def test_1(self):
        pass
