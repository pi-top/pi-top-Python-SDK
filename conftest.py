from os import environ
from sys import modules
from unittest.mock import Mock

for module in [
    "pitop.common.ptdm.zmq",
    "zmq",
    "smbus2",
    "smbus",
    "atexit",
]:
    modules[module] = Mock()

# use gpiozero fake pins
environ["GPIOZERO_PIN_FACTORY"] = "mock"
