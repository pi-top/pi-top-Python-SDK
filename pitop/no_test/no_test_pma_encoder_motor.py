from math import pi
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


class EncoderMotorTestCase(TestCase):

    def test_internal_attributes_on_instance(self):
        """Default values of attributes are set when creating object."""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        self.assertEquals(wheel.wheel_diameter, 0.075)
        self.assertEquals(round(wheel.wheel_circumference, 3), 0.236)
        self.assertEquals(wheel.forward_direction, ForwardDirection.CLOCKWISE)

    @patch("pitop.pma.EncoderMotor.max_rpm", 142)
    @patch("pitop.pma.EncoderMotor.wheel_circumference", 0.075)
    def test_max_speed(self):
        """Max speed calculation based on max rpm."""

        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        self.assertEquals(round(wheel.max_speed, 3), 0.177)

    @patch("pitop.pma.EncoderMotor.set_target_speed")
    def test_forward_uses_correct_direction(self, mock_set_target_speed):
        """Forward method uses correct direction when calling
        set_target_speed."""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        wheel.forward(1)
        mock_set_target_speed.assert_called_once_with(1, Direction.FORWARD, 0.0)

    @patch("pitop.pma.EncoderMotor.set_target_speed")
    def test_backward_uses_correct_direction(self, mock_set_target_speed):
        """Backward method uses correct direction when calling
        set_target_speed."""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        wheel.backward(1)
        mock_set_target_speed.assert_called_once_with(1, Direction.BACK, 0.0)

    def test_wheel_diameter_change_updates_wheel_circumference(self):
        """Updating wheel diameter changes wheel circumference."""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        initial_circumference = wheel.wheel_circumference

        new_diameter = 0.5
        wheel.wheel_diameter = new_diameter
        self.assertNotEqual(wheel.wheel_circumference, initial_circumference)
        self.assertEquals(wheel.wheel_circumference, new_diameter * pi)

    def test_wheel_diameter_cant_be_zero_or_negative(self):
        """Wheel diameter must be higher than zero."""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        for invalid_diameter in (-10, 0):
            with self.assertRaises(ValueError):
                wheel.wheel_diameter = invalid_diameter

    @patch("pitop.pma.EncoderMotor.set_target_rpm")
    def test_set_target_speed_calls_set_target_rpm_with_correct_params(self, set_target_rpm_mock):
        """set_target_speed calls set_target_rpm with correct params."""

        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        speed_test_data = [
            (0.1, Direction.FORWARD, 1),
            (0.1, Direction.BACK, -50.3),
            (-0.05, Direction.FORWARD, 0),
            (0, Direction.BACK, 55),
        ]

        for speed, direction, distance in speed_test_data:
            target_speed_in_rpm = 60.0 * (speed / wheel.wheel_circumference)
            target_motor_rotations = distance / wheel.wheel_circumference

            wheel.set_target_speed(speed, direction, distance)
            set_target_rpm_mock.assert_called_with(target_speed_in_rpm, direction, target_motor_rotations)

    @patch("pitop.pma.EncoderMotor.set_target_rpm")
    def test_set_target_speed_fails_when_requesting_an_out_of_range_speed(self, set_target_rpm_mock):
        """set_target_speed fails if requesting a value out of range."""

        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        speed_test_data = [
            (1, Direction.FORWARD, 1),
            (1, Direction.BACK, -50.3),
            (-33, Direction.FORWARD, 0),
            (10, Direction.BACK, 55),
        ]

        for speed, direction, distance in speed_test_data:
            target_speed_in_rpm = speed * 60.0 / wheel.wheel_circumference
            target_motor_rotations = distance / wheel.wheel_circumference

            with self.assertRaises(ValueError):
                wheel.set_target_speed(speed, direction, distance)
                set_target_rpm_mock.assert_called_with(target_speed_in_rpm, direction, target_motor_rotations)
