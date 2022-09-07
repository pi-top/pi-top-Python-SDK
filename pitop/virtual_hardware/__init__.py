from os import environ
import sys
from unittest.mock import patch

from gpiozero import Device
from gpiozero.pins.mock import MockFactory
import Mock.GPIO


using_virtual_hardware = False


def use_virtual_hardware():
    global using_virtual_hardware

    environ["GPIOZERO_PIN_FACTORY"] = "mock"

    sys.modules["RPi.GPIO"] = Mock.GPIO

    patch("pitop.system.pitop.SupportsMiniscreen").start()
    patch("pitop.system.pitop.SupportsBattery").start()

    using_virtual_hardware = True


if environ.get("PITOP_VIRTUAL_HARDWARE") is not None:
    use_virtual_hardware()
