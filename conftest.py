import gc
from os import environ
from sys import modules
from unittest.mock import Mock

import pytest

for module in [
    "pitop.common.ptdm.zmq",
    "imageio",
    "zmq",
    "smbus2",
    "smbus",
    "atexit",
    "logging",
]:
    modules[module] = Mock()

# use gpiozero fake pins
environ["GPIOZERO_PIN_FACTORY"] = "mock"


@pytest.fixture(autouse=True)
def ensure_gc():
    gc.collect()
