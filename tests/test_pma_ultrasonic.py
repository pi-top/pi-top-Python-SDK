from unittest import TestCase
from unittest.mock import Mock, patch

from pitop.pma.ultrasonic_sensor import UltrasonicSensor


class UltrasonicSensorRPIMock(Mock):
    pass


class UltrasonicSensorMCUMock(Mock):
    pass


@patch("pitop.pma.ultrasonic_sensor.UltrasonicSensorRPI", new=UltrasonicSensorRPIMock)
@patch("pitop.pma.ultrasonic_sensor.UltrasonicSensorMCU", new=UltrasonicSensorMCUMock)
class UltrasonicSensorTestCase(TestCase):
    def test_analog_port_gives_mcu_device(self):
        for port in ("A1", "A3"):
            ultrasonic_sensor = UltrasonicSensor(port)
            assert isinstance(
                ultrasonic_sensor._UltrasonicSensor__ultrasonic_device,
                UltrasonicSensorMCUMock,
            )

    def test_digital_port_gives_rpi_device(self):
        for port in [f"D{i}" for i in range(0, 8)]:
            ultrasonic_sensor = UltrasonicSensor(port)
            assert isinstance(
                ultrasonic_sensor._UltrasonicSensor__ultrasonic_device,
                UltrasonicSensorRPIMock,
            )

    def test_threshold_distance(self):
        for port in ("A1", "D1"):
            new_value = 0.5
            ultrasonic_sensor = UltrasonicSensor(port)
            ultrasonic_sensor.threshold_distance = new_value
            self.assertEqual(new_value, ultrasonic_sensor.threshold_distance)
