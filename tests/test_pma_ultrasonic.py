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
    "pitopcommon.i2c_device",
    "pitopcommon.logger",
    "pitopcommon.singleton",
]
for module in modules_to_patch:
    modules[module] = Mock()

from pitop.pma.ultrasonic_sensor import UltrasonicSensor
from pitop.pma.ultrasonic_sensor_base import (
    UltrasonicSensorRPI,
    UltrasonicSensorMCU,
)


# Avoid getting the mocked modules in other tests
for patched_module in modules_to_patch:
    del modules[patched_module]


class UltrasonicSensorTestCase(TestCase):

    def test_analog_port_gives_mcu_device(self):
        for port in ("A1", "A3"):
            ultrasonic_sensor = UltrasonicSensor(port)
            self.assertIsInstance(ultrasonic_sensor._UltrasonicSensor__ultrasonic_device, UltrasonicSensorMCU)

    def test_digital_port_gives_rpi_device(self):
        for port in [f'D{i}'for i in range(0, 8)]:
            ultrasonic_sensor = UltrasonicSensor(port)
            self.assertIsInstance(ultrasonic_sensor._UltrasonicSensor__ultrasonic_device, UltrasonicSensorRPI)
    