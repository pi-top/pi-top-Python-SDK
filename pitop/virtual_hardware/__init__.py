from os import environ
import sys
from unittest.mock import patch

from gpiozero import Device
from gpiozero.pins.mock import MockFactory
import Mock.GPIO


__using_virtual_hardware = False


def is_virtual_hardware():
    return __using_virtual_hardware


def use_virtual_hardware():
    global __using_virtual_hardware

    environ["GPIOZERO_PIN_FACTORY"] = "mock"

    sys.modules["RPi.GPIO"] = Mock.GPIO

    patch("pitop.system.pitop.SupportsMiniscreen").start()
    patch("pitop.system.pitop.SupportsBattery").start()

    __using_virtual_hardware = True


if environ.get("PITOP_VIRTUAL_HARDWARE") is not None:
    use_virtual_hardware()