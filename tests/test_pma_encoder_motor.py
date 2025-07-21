from math import pi
from unittest import TestCase
from unittest.mock import patch

from pitop.pma.encoder_motor import EncoderMotor
from pitop.pma.parameters import BrakingType, Direction, ForwardDirection


class EncoderMotorTestCase(TestCase):
    def test_internal_attributes_on_instance(self):
        """Default values of attributes are set when creating object."""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST,
        )

        self.assertEqual(wheel.wheel_diameter, 0.07)
        self.assertEqual(round(wheel.wheel_circumference, 3), 0.22)
        self.assertEqual(wheel.forward_direction, ForwardDirection.CLOCKWISE)

    @patch("pitop.pma.EncoderMotor.max_rpm", 142)
    @patch("pitop.pma.EncoderMotor.wheel_circumference", 0.075)
    def test_max_speed(self):
        """Max speed calculation based on max rpm."""

        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST,
        )

        self.assertEqual(round(wheel.max_speed, 3), 0.177)

    @patch("pitop.pma.EncoderMotor.set_target_speed")
    def test_forward_uses_correct_direction(self, mock_set_target_speed):
        """Forward method uses correct direction when calling
        set_target_speed."""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST,
        )

        wheel.forward(1)
        mock_set_target_speed.assert_called_once_with(1, Direction.FORWARD, 0.0)

    @patch("pitop.pma.EncoderMotor.set_target_speed")
    def test_backward_uses_correct_direction(self, mock_set_target_speed):
        """Backward method uses correct direction when calling
        set_target_speed."""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST,
        )

        wheel.backward(1)
        mock_set_target_speed.assert_called_once_with(1, Direction.BACK, 0.0)

    def test_wheel_diameter_change_updates_wheel_circumference(self):
        """Updating wheel diameter changes wheel circumference."""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST,
        )

        initial_circumference = wheel.wheel_circumference

        new_diameter = 0.5
        wheel.wheel_diameter = new_diameter
        self.assertNotEqual(wheel.wheel_circumference, initial_circumference)
        self.assertEqual(wheel.wheel_circumference, new_diameter * pi)

    def test_wheel_diameter_cant_be_zero_or_negative(self):
        """Wheel diameter must be higher than zero."""
        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST,
        )

        for invalid_diameter in (-10, 0):
            with self.assertRaises(ValueError):
                wheel.wheel_diameter = invalid_diameter

    @patch("pitop.pma.EncoderMotor.set_target_rpm")
    def test_set_target_speed_calls_set_target_rpm_with_correct_params(
        self, set_target_rpm_mock
    ):
        """set_target_speed calls set_target_rpm with correct params."""

        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST,
        )

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
            set_target_rpm_mock.assert_called_with(
                target_speed_in_rpm, direction, target_motor_rotations
            )

    @patch("pitop.pma.EncoderMotor.set_target_rpm")
    def test_set_target_speed_fails_when_requesting_an_out_of_range_speed(
        self, set_target_rpm_mock
    ):
        """set_target_speed fails if requesting a value out of range."""

        wheel = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST,
        )

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
                set_target_rpm_mock.assert_called_with(
                    target_speed_in_rpm, direction, target_motor_rotations
                )

    @patch("pitop.pma.encoder_motor.EncoderMotorController.odometer")
    def test_reset_rotation_counter_method(self, mock_odometer):
        """Test that setting rotation_counter sets the offset correctly."""
        # Mock odometer call
        mock_odometer.return_value = 456

        encoder_motor = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST,
        )

        # Initial value is based on the odometer
        expected_rotations = round((456 / encoder_motor.MMK_STANDARD_GEAR_RATIO), 1)
        self.assertEqual(encoder_motor.rotation_counter, expected_rotations)

        # Set rotation_counter property to a few values; the property will now return the same value
        encoder_motor.reset_rotation_counter()
        self.assertEqual(encoder_motor.rotation_counter, 0)

        encoder_motor.reset_rotation_counter(100)
        self.assertEqual(encoder_motor.rotation_counter, 100)

        # When the EncoderMotor moves, the odometer returns a new value, which causes the rotation counter to be updated
        mock_odometer.return_value = 1500.0
        # Calculate expected_rotations based on the new offset, based on the current and previous odometer readings
        expected_rotations = round(
            100 + (1500.0 - 456) / encoder_motor.MMK_STANDARD_GEAR_RATIO, 1
        )
        self.assertEqual(encoder_motor.rotation_counter, expected_rotations)

        # Make sure this still works when the odometer moves in the opposite direction and returns a negative value
        mock_odometer.return_value = -1000.0
        expected_rotations = round(
            expected_rotations
            + (-1000.0 - 1500) / encoder_motor.MMK_STANDARD_GEAR_RATIO,
            1,
        )
        self.assertEqual(encoder_motor.rotation_counter, expected_rotations)

        # Setter also handles negative values
        encoder_motor.reset_rotation_counter(-100)
        self.assertEqual(encoder_motor.rotation_counter, -100)

    @patch("pitop.pma.encoder_motor.EncoderMotorController.odometer")
    def test_reset_rotation_counter_error_handling(self, mock_odometer):
        """Test that setting rotation_counter setter raises an error when given an invalid value."""
        # Mock odometer call
        mock_odometer.return_value = 0

        encoder_motor = EncoderMotor(
            port_name="M1",
            forward_direction=ForwardDirection.CLOCKWISE,
            braking_type=BrakingType.COAST,
        )

        for invalid_value in (
            "100",
            b"123",
            True,
            False,
            [123, 456],
            [],
            (),
            (1231, "asd"),
            None,
            lambda x: x,
        ):
            print(f"Testing with invalid_value: {invalid_value!r}")
            with self.assertRaises(ValueError):
                encoder_motor.reset_rotation_counter(invalid_value)
