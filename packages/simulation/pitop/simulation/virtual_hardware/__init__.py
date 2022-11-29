import sys
from os import environ

from .pitop import mock_pitop
from .vendor.Mock import GPIO as Mock_GPIO

__using_virtual_hardware = False


def is_virtual_hardware():
    return __using_virtual_hardware


def use_virtual_hardware():
    global __using_virtual_hardware

    environ["GPIOZERO_PIN_FACTORY"] = "mock"
    sys.modules["RPi.GPIO"] = Mock_GPIO

    mock_pitop()

    __using_virtual_hardware = True


if environ.get("PITOP_VIRTUAL_HARDWARE") is not None:
    use_virtual_hardware()
