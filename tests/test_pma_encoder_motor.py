from unittest.mock import Mock
from sys import modules

modules["gpiozero"] = Mock()
modules["gpiozero.exc"] = Mock()
modules["cv2"] = Mock()
modules["numpy"] = Mock()
modules["pitopcommon.smbus_device"] = Mock()
modules["pitopcommon.logger"] = Mock()
modules["pitopcommon.singleton"] = Mock()
modules["pitop.pma.ultrasonic_sensor"] = Mock()

from pitop.pma.encoder_motor import EncoderMotor
from pitop.pma.parameters import (
    BrakingType,
    ForwardDirection,
    Direction
)
from unittest import TestCase, skip
from math import pi


@skip
class EncoderMotorTestCase(TestCase):
    def test_internal_attributes_on_instance(self):
        """Default values of attributes are set when creating object"""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        self.assertEquals(wheel.wheel_diameter, 0.075)
        self.assertEquals(round(wheel._wheel_circumference, 3), 0.201)
        self.assertEquals(wheel.forward_direction, ForwardDirection.CLOCKWISE)

    def test_max_speed(self):
        """Max speed calculation based on max rpm"""
        EncoderMotor.max_rpm = Mock()
        EncoderMotor.max_rpm = 142
        EncoderMotor._wheel_circumference = 0.075

        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        self.assertEquals(round(wheel.max_speed, 3), 0.476)

    def test_forward_uses_correct_direction(self):
        """Forward method uses correct direction when calling set_target_speed"""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        mock_set_target_speed = wheel.set_target_speed = Mock()
        wheel.forward(1)
        mock_set_target_speed.assert_called_once_with(1, Direction.FORWARD, 0.0)

    def test_backward_uses_correct_direction(self):
        """Backward method uses correct direction when calling set_target_speed"""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        mock_set_target_speed = wheel.set_target_speed = Mock()
        wheel.backward(1)
        mock_set_target_speed.assert_called_once_with(1, Direction.BACK, 0.0)

    def test_wheel_diameter_change_updates_wheel_circumference(self):
        """Updating wheel diameter changes wheel circumference"""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        initial_circumference = wheel._wheel_circumference

        new_diameter = 0.5
        wheel.wheel_diameter = new_diameter
        self.assertNotEqual(wheel._wheel_circumference, initial_circumference)
        self.assertEquals(wheel._wheel_circumference, new_diameter * pi)

    def test_wheel_diameter_cant_be_zero_or_negative(self):
        """Wheel diameter must be higher than zero"""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        for invalid_diameter in (-10, 0):
            with self.assertRaises(ValueError):
                wheel.wheel_diameter = invalid_diameter

    def test_set_target_speed_calls_set_target_rpm_with_correct_params(self):
        """set_target_speed calls set_target_rpm with correct params"""
        set_target_rpm_mock = EncoderMotor.set_target_rpm = Mock()

        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST)

        speed_test_data = [
            (0.1, Direction.FORWARD, 1),
            (0.1, Direction.BACK, -50.3),
            (-0.33, Direction.FORWARD, 0),
            (0, Direction.BACK, 55),
        ]

        for speed, direction, distance in speed_test_data:
            target_speed_in_rpm = speed * 60.0 / wheel._wheel_circumference
            target_motor_rotations = distance / wheel._wheel_circumference

            wheel.set_target_speed(speed, direction, distance)
            set_target_rpm_mock.assert_called_with(target_speed_in_rpm, direction, target_motor_rotations)

    def test_set_target_speed_fails_when_requesting_an_out_of_range_speed(self):
        """set_target_speed fails if requesting a value out of range"""
        set_target_rpm_mock = EncoderMotor.set_target_rpm = Mock()

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
            target_speed_in_rpm = speed * 60.0 / wheel._wheel_circumference
            target_motor_rotations = distance / wheel._wheel_circumference

            with self.assertRaises(ValueError):
                wheel.set_target_speed(speed, direction, distance)
                set_target_rpm_mock.assert_called_with(target_speed_in_rpm, direction, target_motor_rotations)
