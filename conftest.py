from os import environ
from sys import modules
from unittest.mock import Mock

for module in [
    "pitop.common.ptdm.zmq",
    "imageio",
    "zmq",
    "smbus2",
    "smbus",
    "atexit",
    "RPi",
    "RPi.GPIO",
    "spidev",
    "pyinotify",
]:
    modules[module] = Mock()

# use gpiozero fake pins
environ["GPIOZERO_PIN_FACTORY"] = "mock"
